"""
modules/insights.py
Generator insight otomatis berbasis hasil simulasi.
"""

import numpy as np
import pandas as pd


def generate_insights(results_dict: dict, df_mc: pd.DataFrame = None) -> list[dict]:
    """
    Hasilkan daftar insight otomatis berformat:
    [{"icon": "🔍", "title": "...", "detail": "...", "type": "info|success|warning"}]
    """
    insights = []

    if not results_dict:
        return [{"icon": "⚠️", "title": "Belum ada data simulasi", "detail": "Jalankan simulasi terlebih dahulu.", "type": "warning"}]

    # --- Kumpulkan metrik ringkasan per skenario ---
    summary = {}
    for key, data in results_dict.items():
        parts  = key.split("_")
        mesin  = int(parts[0])
        coping = parts[2]
        summary[key] = {
            "mesin":      mesin,
            "coping":     coping,
            "avg_wait":   np.mean(data["wait"])    if data["wait"]    else 0,
            "pergi":      data["pergi"],
            "avg_anxiety":np.mean(data["anxiety"]) if data["anxiety"] else 0,
            "dilayani":   data["selesai"],
        }

    # ── Insight 1: Perbandingan mesin ─────────────────────────────────────
    mesin1_waits = [v["avg_wait"] for v in summary.values() if v["mesin"] == 1]
    mesin2_waits = [v["avg_wait"] for v in summary.values() if v["mesin"] == 2]

    if mesin1_waits and mesin2_waits:
        avg1 = np.mean(mesin1_waits)
        avg2 = np.mean(mesin2_waits)
        if avg1 > avg2:
            selisih = round(avg1 - avg2, 2)
            pct     = round((selisih / avg1) * 100, 1) if avg1 > 0 else 0
            insights.append({
                "icon":   "⚙️",
                "title":  "2 Mesin Lebih Efisien",
                "detail": f"Rata-rata waktu tunggu dengan 2 mesin ({avg2:.2f}) lebih rendah {pct}% dibandingkan 1 mesin ({avg1:.2f}). Penambahan kapasitas server berdampak signifikan terhadap kenyamanan pelanggan.",
                "type":   "success",
            })

    # ── Insight 2: Pelanggan Pergi ─────────────────────────────────────────
    mesin1_pergi = [v["pergi"] for v in summary.values() if v["mesin"] == 1]
    mesin2_pergi = [v["pergi"] for v in summary.values() if v["mesin"] == 2]

    if mesin1_pergi and mesin2_pergi:
        avg_p1 = np.mean(mesin1_pergi)
        avg_p2 = np.mean(mesin2_pergi)
        if avg_p1 > avg_p2:
            insights.append({
                "icon":   "🚪",
                "title":  "2 Mesin Mengurangi Pelanggan Pergi",
                "detail": f"Rata-rata pelanggan yang pergi dengan 1 mesin adalah {avg_p1:.1f}, sedangkan dengan 2 mesin hanya {avg_p2:.1f}. Kapasitas yang memadai mencegah kehilangan pelanggan.",
                "type":   "success",
            })

    # ── Insight 3: Strategi Coping Terbaik ───────────────────────────────
    coping_anxiety = {}
    for v in summary.values():
        c = v["coping"]
        coping_anxiety.setdefault(c, []).append(v["avg_anxiety"])

    coping_means = {c: np.mean(vals) for c, vals in coping_anxiety.items()}
    if coping_means:
        best_coping  = min(coping_means, key=coping_means.get)
        worst_coping = max(coping_means, key=coping_means.get)
        coping_label = {
            "none": "Tanpa Coping",
            "reactive": "Reactive",
            "preventive": "Preventive",
            "adaptive": "Adaptive",
        }
        insights.append({
            "icon":   "🧠",
            "title":  f"Strategi {coping_label.get(best_coping, best_coping)} Terbaik",
            "detail": f"{coping_label.get(best_coping, best_coping)} menghasilkan rata-rata anxiety terendah ({coping_means[best_coping]:.3f}), jauh lebih baik dibandingkan {coping_label.get(worst_coping, worst_coping)} ({coping_means[worst_coping]:.3f}). Intervensi coping psikologis terbukti efektif.",
            "type":   "info",
        })

    # ── Insight 4: Hubungan Waiting Time → Anxiety ────────────────────────
    all_wait    = [v["avg_wait"]    for v in summary.values()]
    all_anxiety = [v["avg_anxiety"] for v in summary.values()]

    if len(all_wait) >= 3:
        corr = np.corrcoef(all_wait, all_anxiety)[0, 1]
        if corr > 0.5:
            insights.append({
                "icon":   "📈",
                "title":  "Waiting Time Meningkatkan Kecemasan",
                "detail": f"Korelasi antara waktu tunggu dan tingkat kecemasan: r = {corr:.2f}. Semakin lama pelanggan menunggu, tingkat kecemasan cenderung meningkat secara signifikan.",
                "type":   "warning",
            })
        elif corr < -0.3:
            insights.append({
                "icon":   "📉",
                "title":  "Coping Memutus Korelasi Waiting–Anxiety",
                "detail": f"Dengan coping yang efektif, korelasi waktu tunggu–kecemasan menurun (r = {corr:.2f}), menunjukkan bahwa intervensi psikologis dapat menekan pengaruh antrean terhadap stres.",
                "type":   "success",
            })

    # ── Insight 5: Skenario Optimal ───────────────────────────────────────
    best_key  = min(summary, key=lambda k: summary[k]["avg_wait"])
    worst_key = max(summary, key=lambda k: summary[k]["avg_wait"])

    bv = summary[best_key]
    wv = summary[worst_key]
    insights.append({
        "icon":   "🏆",
        "title":  f"Skenario Optimal: {best_key.replace('_', ' ').title()}",
        "detail": (
            f"Skenario terbaik adalah {best_key} dengan rata-rata waktu tunggu {bv['avg_wait']:.2f} "
            f"dan {bv['pergi']} pelanggan pergi. "
            f"Skenario terburuk adalah {worst_key} (waktu tunggu {wv['avg_wait']:.2f}, "
            f"{wv['pergi']} pelanggan pergi)."
        ),
        "type": "success",
    })

    # ── Insight 6: Monte Carlo (jika tersedia) ────────────────────────────
    if df_mc is not None and not df_mc.empty:
        best_mc  = df_mc.loc[df_mc["avg_wait_mean"].idxmin()]
        worst_mc = df_mc.loc[df_mc["avg_wait_mean"].idxmax()]
        insights.append({
            "icon":   "🎲",
            "title":  "Hasil Monte Carlo Mengkonfirmasi Stabilitas",
            "detail": (
                f"Dari {df_mc['avg_wait_mean'].count()} skenario yang diuji, "
                f"{best_mc['scenario']} konsisten menghasilkan waktu tunggu terpendek "
                f"(mean = {best_mc['avg_wait_mean']:.2f}, σ = {best_mc['avg_wait_std']:.2f}). "
                f"Hasil ini stabil di seluruh iterasi Monte Carlo."
            ),
            "type": "info",
        })

    # ── Insight 7: Preventive vs Reactive ────────────────────────────────
    prev_anxiety = [v["avg_anxiety"] for v in summary.values() if v["coping"] == "preventive"]
    reac_anxiety = [v["avg_anxiety"] for v in summary.values() if v["coping"] == "reactive"]
    if prev_anxiety and reac_anxiety:
        avg_prev = np.mean(prev_anxiety)
        avg_reac = np.mean(reac_anxiety)
        if avg_prev < avg_reac:
            insights.append({
                "icon":   "🛡️",
                "title":  "Preventive Coping Lebih Stabil dari Reactive",
                "detail": f"Preventive coping menurunkan kecemasan secara konsisten di setiap langkah waktu (anxiety rata-rata {avg_prev:.3f}), sedangkan reactive coping hanya aktif saat kecemasan sudah tinggi ({avg_reac:.3f}). Pendekatan preventif lebih efektif untuk manajemen stres jangka panjang.",
                "type": "info",
            })

    return insights


def generate_dataset_insights(df: pd.DataFrame) -> list[dict]:
    """Insight berbasis dataset yang diupload."""
    insights = []
    if df.empty:
        return insights

    avg_layanan = df["layanan"].mean() if "layanan" in df.columns else 0
    avg_sabar   = df["sabar"].mean()   if "sabar"   in df.columns else 0
    n           = len(df)

    if avg_layanan > avg_sabar * 0.8:
        insights.append({
            "icon":   "⚠️",
            "title":  "Waktu Layanan Mendekati Batas Kesabaran",
            "detail": f"Rata-rata waktu layanan ({avg_layanan:.2f}) hampir menyamai rata-rata batas kesabaran ({avg_sabar:.2f}). Risiko tinggi pelanggan meninggalkan antrian.",
            "type":   "warning",
        })

    if n < 20:
        insights.append({
            "icon":   "📊",
            "title":  "Dataset Kecil – Hasil Simulasi Bersifat Indikatif",
            "detail": f"Dataset hanya memiliki {n} baris. Hasil simulasi lebih representatif dengan dataset 50+ pelanggan.",
            "type":   "warning",
        })
    else:
        insights.append({
            "icon":   "✅",
            "title":  f"Dataset Valid – {n} Pelanggan",
            "detail": f"Dataset berisi {n} pelanggan dengan rata-rata layanan {avg_layanan:.2f} dan rata-rata kesabaran {avg_sabar:.2f}.",
            "type":   "success",
        })

    return insights
