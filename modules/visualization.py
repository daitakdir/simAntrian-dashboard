"""
modules/visualization.py
Semua fungsi visualisasi Plotly untuk dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Palet warna konsisten
COLORS = {
    "none":       "#EF4444",
    "reactive":   "#F59E0B",
    "preventive": "#10B981",
    "adaptive":   "#6366F1",
    "1_mesin":    "#3B82F6",
    "2_mesin":    "#8B5CF6",
}

COPING_LABELS = {
    "none":       "Tanpa Coping",
    "reactive":   "Reactive",
    "preventive": "Preventive",
    "adaptive":   "Adaptive",
}

PLOTLY_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor":  "rgba(17,17,34,0.6)",
    "font":          {"color": "#E2E8F0", "family": "Inter, sans-serif"},
    "xaxis":         {"gridcolor": "rgba(255,255,255,0.08)", "linecolor": "rgba(255,255,255,0.15)"},
    "yaxis":         {"gridcolor": "rgba(255,255,255,0.08)", "linecolor": "rgba(255,255,255,0.15)"},
}


def _apply_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_THEME)
    return fig


# ─── 1. Line Chart Anxiety ────────────────────────────────────────────────────
def fig_anxiety_line(results_dict: dict, selected_scenarios: list) -> go.Figure:
    """
    Line chart perbandingan tingkat kecemasan antar skenario terpilih.
    results_dict: {scenario_key: sim_data}
    """
    fig = go.Figure()
    for key in selected_scenarios:
        if key not in results_dict:
            continue
        anxiety = results_dict[key].get("anxiety", [])
        if not anxiety:
            continue
        mesin, coping = _parse_key(key)
        color = COLORS.get(coping, "#94A3B8")
        label = f"{mesin} Mesin – {COPING_LABELS.get(coping, coping)}"
        fig.add_trace(go.Scatter(
            y=anxiety,
            mode="lines",
            name=label,
            line=dict(color=color, width=1.8),
            opacity=0.9,
        ))
    fig.update_layout(
        title="Dinamika Tingkat Kecemasan Pelanggan",
        xaxis_title="Langkah Waktu Simulasi",
        yaxis_title="Tingkat Kecemasan (A)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode="x unified",
        height=420,
    )
    return _apply_theme(fig)


# ─── 2. Line Chart Waiting Time (kumulatif) ───────────────────────────────────
def fig_waiting_line(results_dict: dict, selected_scenarios: list) -> go.Figure:
    fig = go.Figure()
    for key in selected_scenarios:
        if key not in results_dict:
            continue
        waits = results_dict[key].get("wait", [])
        if not waits:
            continue
        mesin, coping = _parse_key(key)
        color = COLORS.get(coping, "#94A3B8")
        label = f"{mesin} Mesin – {COPING_LABELS.get(coping, coping)}"
        fig.add_trace(go.Scatter(
            y=waits,
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2),
            marker=dict(size=4),
        ))
    fig.update_layout(
        title="Waktu Tunggu Pelanggan yang Dilayani",
        xaxis_title="Urutan Pelanggan Dilayani",
        yaxis_title="Waktu Tunggu",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode="x unified",
        height=420,
    )
    return _apply_theme(fig)


# ─── 3. Histogram Anxiety ─────────────────────────────────────────────────────
def fig_anxiety_histogram(results_dict: dict, selected_scenarios: list) -> go.Figure:
    fig = go.Figure()
    for key in selected_scenarios:
        if key not in results_dict:
            continue
        anxiety = results_dict[key].get("anxiety", [])
        if not anxiety:
            continue
        mesin, coping = _parse_key(key)
        label = f"{mesin} Mesin – {COPING_LABELS.get(coping, coping)}"
        fig.add_trace(go.Histogram(
            x=anxiety,
            name=label,
            opacity=0.7,
            marker_color=COLORS.get(coping, "#94A3B8"),
            nbinsx=30,
        ))
    fig.update_layout(
        title="Distribusi Tingkat Kecemasan",
        xaxis_title="Nilai Kecemasan",
        yaxis_title="Frekuensi",
        barmode="overlay",
        height=380,
    )
    return _apply_theme(fig)


# ─── 4. Histogram Waiting Time ───────────────────────────────────────────────
def fig_waiting_histogram(results_dict: dict, selected_scenarios: list) -> go.Figure:
    fig = go.Figure()
    for key in selected_scenarios:
        if key not in results_dict:
            continue
        waits = results_dict[key].get("wait", [])
        if not waits:
            continue
        mesin, coping = _parse_key(key)
        label = f"{mesin} Mesin – {COPING_LABELS.get(coping, coping)}"
        fig.add_trace(go.Histogram(
            x=waits,
            name=label,
            opacity=0.7,
            marker_color=COLORS.get(coping, "#94A3B8"),
            nbinsx=25,
        ))
    fig.update_layout(
        title="Distribusi Waktu Tunggu",
        xaxis_title="Waktu Tunggu",
        yaxis_title="Frekuensi",
        barmode="overlay",
        height=380,
    )
    return _apply_theme(fig)


# ─── 5. Boxplot Anxiety ───────────────────────────────────────────────────────
def fig_anxiety_boxplot(results_dict: dict) -> go.Figure:
    fig = go.Figure()
    for key, data in results_dict.items():
        anxiety = data.get("anxiety", [])
        if not anxiety:
            continue
        mesin, coping = _parse_key(key)
        label = f"{mesin}M–{COPING_LABELS.get(coping, coping)}"
        fig.add_trace(go.Box(
            y=anxiety,
            name=label,
            marker_color=COLORS.get(coping, "#94A3B8"),
            boxmean=True,
        ))
    fig.update_layout(
        title="Boxplot Tingkat Kecemasan per Skenario",
        yaxis_title="Tingkat Kecemasan",
        height=420,
        showlegend=False,
    )
    return _apply_theme(fig)


# ─── 6. Boxplot Waiting Time ─────────────────────────────────────────────────
def fig_waiting_boxplot(results_dict: dict) -> go.Figure:
    fig = go.Figure()
    for key, data in results_dict.items():
        waits = data.get("wait", [])
        if not waits:
            continue
        mesin, coping = _parse_key(key)
        label = f"{mesin}M–{COPING_LABELS.get(coping, coping)}"
        fig.add_trace(go.Box(
            y=waits,
            name=label,
            marker_color=COLORS.get(coping, "#94A3B8"),
            boxmean=True,
        ))
    fig.update_layout(
        title="Boxplot Waktu Tunggu per Skenario",
        yaxis_title="Waktu Tunggu",
        height=420,
        showlegend=False,
    )
    return _apply_theme(fig)


# ─── 7. Comparison Bar Chart (Pergi & Waktu Tunggu) ──────────────────────────
def fig_comparison_bar(results_dict: dict) -> go.Figure:
    labels, wait_vals, pergi_vals, colors_list = [], [], [], []
    for key, data in results_dict.items():
        mesin, coping = _parse_key(key)
        labels.append(f"{mesin}M–{COPING_LABELS.get(coping, coping)}")
        wait_vals.append(np.mean(data["wait"]) if data["wait"] else 0)
        pergi_vals.append(data["pergi"])
        colors_list.append(COLORS.get(coping, "#94A3B8"))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Rata-rata Waktu Tunggu",
        x=labels,
        y=wait_vals,
        marker_color=colors_list,
        opacity=0.85,
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        name="Pelanggan Pergi",
        x=labels,
        y=pergi_vals,
        mode="lines+markers",
        marker=dict(size=10, symbol="diamond"),
        line=dict(color="#F472B6", width=2.5),
        yaxis="y2",
    ))
    fig.update_layout(
        title="Perbandingan Waktu Tunggu & Pelanggan Pergi (Semua Skenario)",
        xaxis_title="Skenario",
        yaxis=dict(title="Rata-rata Waktu Tunggu", gridcolor="rgba(255,255,255,0.08)"),
        yaxis2=dict(
            title="Jumlah Pelanggan Pergi",
            overlaying="y",
            side="right",
            gridcolor="rgba(0,0,0,0)",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=450,
        barmode="group",
    )
    return _apply_theme(fig)


# ─── 8. Monte Carlo Results Chart ─────────────────────────────────────────────
def fig_monte_carlo(df_mc: pd.DataFrame) -> tuple:
    """
    Kembalikan dua figure: bar CI waktu tunggu dan bar CI pelanggan pergi.
    """
    if df_mc.empty:
        return go.Figure(), go.Figure()

    scenarios = df_mc["scenario"].tolist()

    # -- Figure A: Waktu Tunggu dengan CI 95% --
    fig_a = go.Figure()
    coping_colors = [COLORS.get(c, "#94A3B8") for c in df_mc["coping"]]

    fig_a.add_trace(go.Bar(
        x=scenarios,
        y=df_mc["avg_wait_mean"],
        error_y=dict(
            type="data",
            symmetric=False,
            array=(df_mc["avg_wait_ci95_high"] - df_mc["avg_wait_mean"]).clip(0).tolist(),
            arrayminus=(df_mc["avg_wait_mean"] - df_mc["avg_wait_ci95_low"]).clip(0).tolist(),
            color="#94A3B8",
        ),
        marker_color=coping_colors,
        opacity=0.85,
        name="Rata-rata Waktu Tunggu",
    ))
    fig_a.update_layout(
        title="Monte Carlo – Rata-rata Waktu Tunggu (CI 95%)",
        xaxis_title="Skenario",
        yaxis_title="Waktu Tunggu",
        xaxis=dict(tickangle=-35),
        height=420,
    )
    _apply_theme(fig_a)

    # -- Figure B: Pelanggan Pergi dengan CI 95% --
    fig_b = go.Figure()
    fig_b.add_trace(go.Bar(
        x=scenarios,
        y=df_mc["pergi_mean"],
        error_y=dict(
            type="data",
            symmetric=False,
            array=(df_mc["pergi_ci95_high"] - df_mc["pergi_mean"]).clip(0).tolist(),
            arrayminus=(df_mc["pergi_mean"] - df_mc["pergi_ci95_low"]).clip(0).tolist(),
            color="#94A3B8",
        ),
        marker_color=coping_colors,
        opacity=0.85,
        name="Pelanggan Pergi",
    ))
    fig_b.update_layout(
        title="Monte Carlo – Jumlah Pelanggan Pergi (CI 95%)",
        xaxis_title="Skenario",
        yaxis_title="Jumlah Pelanggan Pergi",
        xaxis=dict(tickangle=-35),
        height=420,
    )
    _apply_theme(fig_b)

    return fig_a, fig_b


# ─── 9. Scatter Anxiety vs Waiting Time ──────────────────────────────────────
def fig_anxiety_vs_wait(results_dict: dict, selected_scenarios: list) -> go.Figure:
    fig = go.Figure()
    for key in selected_scenarios:
        if key not in results_dict:
            continue
        data  = results_dict[key]
        waits   = data.get("wait", [])
        anxiety = data.get("anxiety", [])
        if not waits or not anxiety:
            continue
        n = min(len(waits), len(anxiety))
        mesin, coping = _parse_key(key)
        label = f"{mesin}M – {COPING_LABELS.get(coping, coping)}"
        fig.add_trace(go.Scatter(
            x=waits[:n],
            y=anxiety[:n],
            mode="markers",
            name=label,
            marker=dict(color=COLORS.get(coping, "#94A3B8"), size=6, opacity=0.7),
        ))
    fig.update_layout(
        title="Korelasi: Waktu Tunggu vs Tingkat Kecemasan",
        xaxis_title="Waktu Tunggu",
        yaxis_title="Tingkat Kecemasan (A)",
        height=420,
    )
    return _apply_theme(fig)


# ─── 10. Agent State Distribution ─────────────────────────────────────────────
def fig_agent_state_pie(sim_data: dict, scenario_label: str) -> go.Figure:
    dilayani = sim_data.get("selesai", 0)
    pergi    = sim_data.get("pergi", 0)
    total    = dilayani + pergi

    fig = go.Figure(go.Pie(
        labels=["Dilayani", "Pergi"],
        values=[dilayani, pergi],
        marker=dict(colors=["#10B981", "#EF4444"]),
        hole=0.45,
        textinfo="percent+label",
    ))
    fig.update_layout(
        title=f"Distribusi State Agen – {scenario_label}",
        annotations=[dict(
            text=f"Total<br>{total}",
            x=0.5, y=0.5,
            font_size=14,
            showarrow=False,
            font_color="#E2E8F0",
        )],
        height=350,
    )
    return _apply_theme(fig)


# ─── Helper ───────────────────────────────────────────────────────────────────
def _parse_key(key: str) -> tuple:
    """'2_mesin_adaptive' → (2, 'adaptive')"""
    parts = key.split("_")
    mesin  = int(parts[0])
    coping = parts[2]
    return mesin, coping
