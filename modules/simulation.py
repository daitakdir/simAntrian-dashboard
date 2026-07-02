"""
modules/simulation.py
Simulasi Antrian Depot Air Minum berbasis SimPy + Agent-Based Modeling
"""

import simpy
import numpy as np
import pandas as pd
import random

# ─── Konstanta Global ────────────────────────────────────────────────────────
D = 0.1                        # Faktor stres per unit antrian
ANXIETY_IMPACT_ON_PATIENCE = 2.0  # Seberapa besar anxiety mengurangi batas sabar efektif


# ─── Fungsi Coping ───────────────────────────────────────────────────────────
def apply_coping(anxiety: float, coping_type: str) -> float:
    """Terapkan strategi coping CBT pada tingkat kecemasan agen."""
    if coping_type == "none":
        return anxiety
    elif coping_type == "reactive":
        if anxiety > 1.5:
            anxiety -= 0.8
        return anxiety
    elif coping_type == "preventive":
        return anxiety - 0.2
    elif coping_type == "adaptive":
        if anxiety > 3.0:
            anxiety -= 1.0
        elif anxiety > 1.5:
            anxiety -= 0.5
        elif anxiety > 0.5:
            anxiety -= 0.1
        return anxiety
    return anxiety


# ─── Kelas Agen Pelanggan ─────────────────────────────────────────────────────
class Pelanggan:
    """
    Representasi agen pelanggan dalam sistem antrian.
    Setiap pelanggan membaca data langsung dari row dataset CSV.
    """

    def __init__(self, env, name, depot, data, coping_type, data_row):
        self.env = env
        self.name = name
        self.depot = depot
        self.data = data
        self.coping_type = coping_type

        # Baca atribut dari dataset
        self.waktu_datang   = float(data_row["kedatangan"])
        self.waktu_layanan  = float(data_row["layanan"])
        self.batas_sabar    = float(data_row["sabar"])
        self.anxiety        = 0.0

        # Rekam state per-agen untuk analisis lanjut
        self.log_anxiety    = []
        self.state          = "tenang"

        # Mulai proses simulasi
        env.process(self.proses())

    def proses(self):
        """Proses utama agen: antri → dilayani / pergi."""
        with self.depot.request() as req:
            while True:
                # Tunggu 1 unit waktu atau resource tersedia
                hasil = yield req | self.env.timeout(1)

                # Hitung anxiety berdasarkan panjang antrian
                S = len(self.depot.queue)
                self.anxiety += S * D
                self.anxiety  = apply_coping(self.anxiety, self.coping_type)
                if self.anxiety < 0:
                    self.anxiety = 0.0

                self.log_anxiety.append(self.anxiety)
                self.data["anxiety"].append(self.anxiety)

                # Hitung batas sabar efektif (anxiety mempersempit kesabaran)
                effective_sabar = self.batas_sabar - (self.anxiety * ANXIETY_IMPACT_ON_PATIENCE)
                effective_sabar = max(1.0, effective_sabar)

                if req in hasil:
                    # Resource berhasil diperoleh → keluar dari loop tunggu
                    break

                # Cek apakah waktu tunggu sudah melewati batas sabar
                if self.env.now - self.waktu_datang > effective_sabar:
                    self.state = "pergi"
                    self.data["pergi"] += 1
                    self.data["agent_logs"].append({
                        "name":         self.name,
                        "state_akhir":  "Pergi",
                        "waktu_datang": self.waktu_datang,
                        "waktu_tunggu": self.env.now - self.waktu_datang,
                        "anxiety_max":  max(self.log_anxiety) if self.log_anxiety else 0,
                        "coping":       self.coping_type,
                    })
                    return

            # Berhasil dilayani
            wait = self.env.now - self.waktu_datang
            self.data["wait"].append(wait)
            self.data["service_times"].append(self.waktu_layanan)

            self.state = "dilayani"
            yield self.env.timeout(self.waktu_layanan)

            self.data["selesai"] += 1
            self.data["agent_logs"].append({
                "name":         self.name,
                "state_akhir":  "Dilayani",
                "waktu_datang": self.waktu_datang,
                "waktu_tunggu": wait,
                "anxiety_max":  max(self.log_anxiety) if self.log_anxiety else 0,
                "coping":       self.coping_type,
            })


# ─── Generator Kedatangan ─────────────────────────────────────────────────────
def generator(env, depot, data, coping_type, dataset_df):
    """Hasilkan pelanggan sesuai urutan kedatangan dari dataset."""
    required = ["pelanggan", "kedatangan", "layanan", "sabar"]
    if not all(c in dataset_df.columns for c in required):
        print(f"[ERROR] Kolom wajib tidak lengkap: {required}")
        return

    dataset_df = dataset_df.sort_values("kedatangan").reset_index(drop=True)

    for _, row in dataset_df.iterrows():
        # Maju waktu simulasi ke waktu kedatangan berikutnya
        gap = max(0.0, float(row["kedatangan"]) - env.now)
        yield env.timeout(gap)

        data["datang"] += 1
        Pelanggan(env, str(row["pelanggan"]), depot, data, coping_type, row)


# ─── Fungsi Utama Simulasi ────────────────────────────────────────────────────
def run_simulasi(
    jumlah_mesin: int,
    coping_type: str,
    seed: int,
    dataset_df: pd.DataFrame,
) -> dict:
    """
    Jalankan satu skenario simulasi.

    Parameters
    ----------
    jumlah_mesin : int
        Kapasitas server (mesin pengisian).
    coping_type : str
        Strategi coping: none | reactive | preventive | adaptive
    seed : int
        Seed RNG untuk reproducibility.
    dataset_df : pd.DataFrame
        Dataset pelanggan dengan kolom: pelanggan, kedatangan, layanan, sabar.

    Returns
    -------
    dict
        datang, selesai, pergi, wait[], service_times[], anxiety[], agent_logs[]
    """
    if dataset_df.empty:
        return {
            "datang": 0, "selesai": 0, "pergi": 0,
            "wait": [], "service_times": [], "anxiety": [], "agent_logs": [],
        }

    random.seed(seed)
    np.random.seed(seed)

    env    = simpy.Environment()
    depot  = simpy.Resource(env, capacity=jumlah_mesin)
    data   = {
        "datang": 0, "selesai": 0, "pergi": 0,
        "wait": [], "service_times": [], "anxiety": [], "agent_logs": [],
    }

    env.process(generator(env, depot, data, coping_type, dataset_df))

    # Batas waktu simulasi = waktu kedatangan terakhir + buffer layanan
    end_time = dataset_df["kedatangan"].max() + dataset_df["layanan"].sum() + 100
    env.run(until=end_time)

    return data


# ─── Jalankan Semua Skenario ──────────────────────────────────────────────────
ALL_SCENARIOS = [
    (1, "none"),
    (1, "reactive"),
    (1, "preventive"),
    (1, "adaptive"),
    (2, "none"),
    (2, "reactive"),
    (2, "preventive"),
    (2, "adaptive"),
]


def run_all_scenarios(dataset_df: pd.DataFrame, seed: int = 42) -> dict:
    """
    Jalankan semua 8 skenario dan kembalikan dict hasilnya.
    Key format: "{mesin}_mesin_{coping}"
    """
    results = {}
    for mesin, coping in ALL_SCENARIOS:
        key = f"{mesin}_mesin_{coping}"
        results[key] = run_simulasi(mesin, coping, seed, dataset_df)
    return results
