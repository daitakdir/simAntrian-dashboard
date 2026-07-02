"""
modules/utils.py
Fungsi utilitas umum untuk dashboard.
"""

import pandas as pd
import numpy as np
import io


# ─── Validasi Dataset ─────────────────────────────────────────────────────────
REQUIRED_COLUMNS = ["pelanggan", "kedatangan", "layanan", "sabar"]


def validate_dataset(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Validasi struktur dataset.
    Returns (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "Dataset kosong."

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return False, f"Kolom berikut tidak ditemukan: **{', '.join(missing)}**. Dataset harus memiliki kolom: {', '.join(REQUIRED_COLUMNS)}."

    # Cek tipe data numerik
    for col in ["kedatangan", "layanan", "sabar"]:
        try:
            pd.to_numeric(df[col], errors="raise")
        except Exception:
            return False, f"Kolom **{col}** harus berisi angka numerik."

    if df["kedatangan"].min() < 0:
        return False, "Kolom **kedatangan** tidak boleh bernilai negatif."

    if df["layanan"].min() <= 0:
        return False, "Kolom **layanan** harus bernilai positif (> 0)."

    if df["sabar"].min() <= 0:
        return False, "Kolom **sabar** harus bernilai positif (> 0)."

    return True, "Dataset valid."


def load_dataset(uploaded_file) -> pd.DataFrame:
    """Load dataset dari Streamlit UploadedFile (CSV)."""
    try:
        content = uploaded_file.read()
        df = pd.read_csv(
            io.BytesIO(content),
            sep=None,
            engine="python",
            encoding="utf-8",
        )
        # Konversi kolom numerik
        for col in ["kedatangan", "layanan", "sabar"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["kedatangan", "layanan", "sabar"])
        return df
    except Exception as e:
        raise ValueError(f"Gagal membaca file CSV: {e}")


# ─── Statistik Dataset ────────────────────────────────────────────────────────
def dataset_stats(df: pd.DataFrame) -> dict:
    """Kembalikan ringkasan statistik dataset."""
    if df.empty:
        return {}
    return {
        "n_pelanggan":   len(df),
        "avg_kedatangan": round(df["kedatangan"].mean(), 2),
        "avg_layanan":    round(df["layanan"].mean(), 2),
        "avg_sabar":      round(df["sabar"].mean(), 2),
        "max_kedatangan": round(df["kedatangan"].max(), 2),
        "min_sabar":      round(df["sabar"].min(), 2),
        "max_sabar":      round(df["sabar"].max(), 2),
        "std_layanan":    round(df["layanan"].std(), 2),
    }


# ─── Ringkasan Simulasi ───────────────────────────────────────────────────────
def sim_summary(data: dict) -> dict:
    """Ringkasan satu hasil simulasi."""
    waits   = data.get("wait", [])
    anxiety = data.get("anxiety", [])
    return {
        "datang":       data.get("datang", 0),
        "dilayani":     data.get("selesai", 0),
        "pergi":        data.get("pergi", 0),
        "avg_wait":     round(np.mean(waits),   4) if waits   else 0,
        "max_wait":     round(np.max(waits),    4) if waits   else 0,
        "avg_anxiety":  round(np.mean(anxiety), 4) if anxiety else 0,
        "max_anxiety":  round(np.max(anxiety),  4) if anxiety else 0,
    }


# ─── Format Label Skenario ────────────────────────────────────────────────────
COPING_ID = {
    "none":       "Tanpa Coping",
    "reactive":   "Reactive",
    "preventive": "Preventive",
    "adaptive":   "Adaptive",
}


def format_scenario_label(key: str) -> str:
    """'2_mesin_adaptive' → '2 Mesin – Adaptive'"""
    parts  = key.split("_")
    mesin  = parts[0]
    coping = parts[2]
    return f"{mesin} Mesin – {COPING_ID.get(coping, coping)}"


def scenario_keys_all() -> list:
    return [
        f"{m}_mesin_{c}"
        for m in [1, 2]
        for c in ["none", "reactive", "preventive", "adaptive"]
    ]


# ─── Export CSV ───────────────────────────────────────────────────────────────
def results_to_dataframe(results_dict: dict) -> pd.DataFrame:
    """Konversi dict hasil simulasi ke DataFrame ringkasan."""
    rows = []
    for key, data in results_dict.items():
        s = sim_summary(data)
        s["scenario"] = key
        s["label"]    = format_scenario_label(key)
        rows.append(s)
    return pd.DataFrame(rows)
