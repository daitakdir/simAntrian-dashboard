"""
modules/montecarlo.py
Uji skenario Monte Carlo untuk simulasi antrian.
"""

import numpy as np
import pandas as pd
from scipy import stats
from modules.simulation import run_simulasi, ALL_SCENARIOS


def run_monte_carlo(
    dataset_df: pd.DataFrame,
    n_iterations: int = 1000,
    progress_callback=None,
) -> pd.DataFrame:
    """
    Jalankan Monte Carlo untuk semua 8 skenario.

    Parameters
    ----------
    dataset_df : pd.DataFrame
        Dataset aktif.
    n_iterations : int
        Jumlah iterasi per skenario.
    progress_callback : callable | None
        Dipanggil dengan (scenario_index, total_scenarios, iteration, n_iterations)
        untuk update progress bar Streamlit.

    Returns
    -------
    pd.DataFrame
        Kolom: scenario, mesin, coping,
               avg_wait_mean, avg_wait_std, avg_wait_ci95_low, avg_wait_ci95_high,
               pergi_mean, pergi_std, pergi_ci95_low, pergi_ci95_high,
               avg_anxiety_mean, avg_anxiety_std
    """
    if dataset_df.empty:
        return pd.DataFrame()

    records = []

    for sc_idx, (mesin, coping) in enumerate(ALL_SCENARIOS):
        avg_waits    = []
        total_pergis = []
        avg_anxieties = []

        for i in range(n_iterations):
            data = run_simulasi(mesin, coping, seed=i + 1, dataset_df=dataset_df)

            if data["wait"]:
                avg_waits.append(np.mean(data["wait"]))
            total_pergis.append(data["pergi"])
            if data["anxiety"]:
                avg_anxieties.append(np.mean(data["anxiety"]))

            if progress_callback:
                progress_callback(sc_idx, len(ALL_SCENARIOS), i, n_iterations)

        # Hitung statistik ringkasan
        def _ci95(arr):
            if len(arr) < 2:
                m = np.mean(arr) if arr else 0
                return (m, m)
            sem = stats.sem(arr)
            if sem == 0 or np.isnan(sem):
                m = np.mean(arr)
                return (m, m)
            ci = stats.t.interval(0.95, df=len(arr) - 1, loc=np.mean(arr), scale=sem)
            if np.isnan(ci[0]) or np.isnan(ci[1]):
                m = np.mean(arr)
                return (m, m)
            return ci

        ci_wait  = _ci95(avg_waits)
        ci_pergi = _ci95(total_pergis)

        records.append({
            "scenario":          f"{mesin}_mesin_{coping}",
            "mesin":             mesin,
            "coping":            coping,
            "avg_wait_mean":     np.mean(avg_waits)     if avg_waits     else 0,
            "avg_wait_std":      np.std(avg_waits)      if avg_waits     else 0,
            "avg_wait_ci95_low": ci_wait[0],
            "avg_wait_ci95_high":ci_wait[1],
            "pergi_mean":        np.mean(total_pergis),
            "pergi_std":         np.std(total_pergis),
            "pergi_ci95_low":    ci_pergi[0],
            "pergi_ci95_high":   ci_pergi[1],
            "avg_anxiety_mean":  np.mean(avg_anxieties) if avg_anxieties else 0,
            "avg_anxiety_std":   np.std(avg_anxieties)  if avg_anxieties else 0,
        })

    return pd.DataFrame(records)


def ttest_two_scenarios(
    dataset_df: pd.DataFrame,
    scenario_a: tuple,
    scenario_b: tuple,
    n_iterations: int = 100,
) -> dict:
    """
    Uji t dua sisi antara dua skenario (mesin, coping).

    Returns
    -------
    dict dengan t_stat, p_value, mean_a, mean_b, interpretation
    """
    waits_a, waits_b = [], []

    for i in range(n_iterations):
        da = run_simulasi(*scenario_a, seed=i + 1, dataset_df=dataset_df)
        db = run_simulasi(*scenario_b, seed=i + 1, dataset_df=dataset_df)
        if da["wait"]:
            waits_a.append(np.mean(da["wait"]))
        if db["wait"]:
            waits_b.append(np.mean(db["wait"]))

    if not waits_a or not waits_b:
        return {"t_stat": 0, "p_value": 1, "mean_a": 0, "mean_b": 0, "interpretation": "Data tidak cukup"}

    t_stat, p_val = stats.ttest_ind(waits_a, waits_b)
    interpretation = (
        "Perbedaan signifikan (p < 0.05)" if p_val < 0.05
        else "Tidak ada perbedaan signifikan (p ≥ 0.05)"
    )

    return {
        "t_stat":         round(t_stat, 4),
        "p_value":        round(p_val, 4),
        "mean_a":         round(np.mean(waits_a), 4),
        "mean_b":         round(np.mean(waits_b), 4),
        "interpretation": interpretation,
    }
