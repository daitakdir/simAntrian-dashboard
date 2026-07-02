"""
app.py  –  Dashboard Simulasi Antrian Depot Air Minum
Universitas Muhammadiyah Malang | Pemodelan dan Simulasi

Jalankan dengan:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import time

# ── Import modul lokal ────────────────────────────────────────────────────────
from modules.simulation   import run_simulasi, run_all_scenarios, ALL_SCENARIOS
from modules.montecarlo   import run_monte_carlo, ttest_two_scenarios
from modules.visualization import (
    fig_anxiety_line, fig_waiting_line,
    fig_anxiety_histogram, fig_waiting_histogram,
    fig_anxiety_boxplot, fig_waiting_boxplot,
    fig_comparison_bar, fig_monte_carlo,
    fig_anxiety_vs_wait, fig_agent_state_pie,
)
from modules.insights import generate_insights, generate_dataset_insights
from modules.utils    import (
    validate_dataset, load_dataset, dataset_stats,
    sim_summary, results_to_dataframe, format_scenario_label,
    scenario_keys_all, COPING_ID,
)

# ═══════════════════════════════════════════════════════════════════════════════
# KONFIGURASI HALAMAN
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SimAntrian – Depot Air Minum",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS KUSTOM
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Variabel Warna ── */
:root {
    --bg-deep:    #0D0D1F;
    --bg-card:    #111128;
    --bg-card2:   #161630;
    --accent1:    #6366F1;
    --accent2:    #818CF8;
    --accent3:    #38BDF8;
    --success:    #10B981;
    --warning:    #F59E0B;
    --danger:     #EF4444;
    --text-main:  #E2E8F0;
    --text-muted: #94A3B8;
    --border:     rgba(99,102,241,0.25);
}

/* ── Latar Belakang ── */
.stApp { background-color: var(--bg-deep); }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0D1F 0%, #111128 100%);
    border-right: 1px solid var(--border);
}

/* ── Tipografi ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: var(--text-main);
}
h1, h2, h3 { color: #F1F5F9; }

/* ── Judul Utama ── */
.dashboard-title {
    background: linear-gradient(135deg, var(--accent1), var(--accent3));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.1rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 0.15rem;
}
.dashboard-subtitle {
    color: var(--text-muted);
    font-size: 0.92rem;
    margin-bottom: 1.5rem;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 0.85rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem 1.1rem 0.85rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.18s, box-shadow 0.18s;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(99,102,241,0.18);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent1), var(--accent3));
    border-radius: 14px 14px 0 0;
}
.kpi-icon  { font-size: 1.5rem; margin-bottom: 0.35rem; }
.kpi-value {
    font-size: 1.65rem;
    font-weight: 800;
    color: #F1F5F9;
    line-height: 1;
}
.kpi-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 0.3rem;
}
.kpi-delta {
    font-size: 0.72rem;
    margin-top: 0.2rem;
    padding: 1px 6px;
    border-radius: 6px;
    display: inline-block;
}
.kpi-delta-up   { background: rgba(16,185,129,0.15); color: #10B981; }
.kpi-delta-down { background: rgba(239,68,68,0.15);  color: #EF4444; }

/* ── Insight Cards ── */
.insight-card {
    background: var(--bg-card);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    border-left: 4px solid var(--accent1);
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
}
.insight-card.success { border-left-color: var(--success); }
.insight-card.warning { border-left-color: var(--warning); }
.insight-card.info    { border-left-color: var(--accent3); }
.insight-icon  { font-size: 1.4rem; flex-shrink: 0; padding-top: 2px; }
.insight-title { font-weight: 700; font-size: 0.95rem; color: #F1F5F9; }
.insight-detail { font-size: 0.84rem; color: var(--text-muted); margin-top: 0.2rem; line-height: 1.55; }

/* ── Divider ── */
.section-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ── Badge Scenario ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-blue   { background: rgba(99,102,241,0.2); color: #818CF8; }
.badge-green  { background: rgba(16,185,129,0.2); color: #34D399; }
.badge-yellow { background: rgba(245,158,11,0.2); color: #FCD34D; }
.badge-red    { background: rgba(239,68,68,0.2);  color: #F87171; }

/* ── Tab Style ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.4rem;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: var(--bg-card);
    border-radius: 8px 8px 0 0;
    color: var(--text-muted);
    border: 1px solid var(--border);
    border-bottom: none;
    padding: 0.5rem 1.1rem;
    font-size: 0.88rem;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card2) !important;
    color: var(--accent2) !important;
    border-color: var(--accent1) !important;
}

/* ── Upload Box ── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 14px !important;
    background: var(--bg-card) !important;
    padding: 1rem !important;
}

/* ── Metric (Streamlit native) ── */
[data-testid="stMetricValue"]   { color: #F1F5F9 !important; }
[data-testid="stMetricLabel"]   { color: var(--text-muted) !important; }
[data-testid="stMetricDelta"]   { font-size: 0.82rem !important; }

/* ── DataFrame ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent1), #4F46E5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
.stButton > button:active { transform: scale(0.98) !important; }

/* ── Selectbox / Slider ── */
.stSelectbox > div,
.stMultiSelect > div { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "df":             None,
        "file_name":      None,
        "results":        {},
        "df_mc":          None,
        "mc_done":        False,
        "sim_done":       False,
        "active_scenario": "1_mesin_none",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <div style="font-size:2.5rem;">💧</div>
        <div style="font-weight:800; font-size:1.1rem; color:#818CF8;">SimAntrian</div>
        <div style="font-size:0.75rem; color:#64748B;">Depot Air Minum | ABM</div>
    </div>
    <hr style="border-color:rgba(99,102,241,0.2); margin:0.75rem 0 1rem;">
    """, unsafe_allow_html=True)

    # ── Upload Dataset ──
    st.markdown("### 📂 Upload Dataset")
    uploaded_file = st.file_uploader(
        "Pilih file CSV",
        type=["csv"],
        help="Dataset harus memiliki kolom: pelanggan, kedatangan, layanan, sabar",
    )

    if uploaded_file is not None:
        try:
            df_temp = load_dataset(uploaded_file)
            is_valid, msg = validate_dataset(df_temp)
            if is_valid:
                st.session_state["df"]        = df_temp
                st.session_state["file_name"] = uploaded_file.name
                st.session_state["sim_done"]  = False
                st.session_state["results"]   = {}
                st.session_state["mc_done"]   = False
                st.success(f"✅ {uploaded_file.name}")
            else:
                st.error(msg)
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("<hr style='border-color:rgba(99,102,241,0.15); margin:0.75rem 0;'>", unsafe_allow_html=True)

    # ── Parameter Simulasi ──
    st.markdown("### ⚙️ Parameter Simulasi")
    sim_mesin  = st.selectbox("Jumlah Mesin", [1, 2], index=0)
    sim_coping = st.selectbox(
        "Strategi Coping",
        ["none", "reactive", "preventive", "adaptive"],
        format_func=lambda x: COPING_ID[x],
    )
    sim_seed   = st.number_input("Seed RNG", value=42, min_value=1, max_value=9999, step=1)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        btn_sim = st.button("▶ Simulasi", use_container_width=True)
    with col_s2:
        btn_all = st.button("🔄 Semua", use_container_width=True, help="Jalankan 8 skenario sekaligus")

    st.markdown("<hr style='border-color:rgba(99,102,241,0.15); margin:0.75rem 0;'>", unsafe_allow_html=True)

    # ── Monte Carlo ──
    st.markdown("### 🎲 Monte Carlo")
    mc_iter = st.slider("Jumlah Iterasi", min_value=50, max_value=1000, value=200, step=50)
    btn_mc  = st.button("▶ Jalankan Monte Carlo", use_container_width=True)

    st.markdown("<hr style='border-color:rgba(99,102,241,0.15); margin:0.75rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.72rem; color:#475569; text-align:center; padding-bottom:1rem;">
        Pemodelan & Simulasi<br>
        Universitas Muhammadiyah Malang<br>
        <span style="color:#6366F1;">2025 / 2026</span>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# AKSI TOMBOL
# ═══════════════════════════════════════════════════════════════════════════════
if btn_sim:
    if st.session_state["df"] is None:
        st.sidebar.error("⚠️ Upload dataset terlebih dahulu.")
    else:
        with st.spinner("Menjalankan simulasi…"):
            key = f"{sim_mesin}_mesin_{sim_coping}"
            res = run_simulasi(sim_mesin, sim_coping, sim_seed, st.session_state["df"])
            st.session_state["results"][key]  = res
            st.session_state["active_scenario"] = key
            st.session_state["sim_done"]      = True
        st.sidebar.success("✅ Simulasi selesai!")

if btn_all:
    if st.session_state["df"] is None:
        st.sidebar.error("⚠️ Upload dataset terlebih dahulu.")
    else:
        with st.spinner("Menjalankan 8 skenario…"):
            all_res = run_all_scenarios(st.session_state["df"], seed=int(sim_seed))
            st.session_state["results"] = all_res
            st.session_state["sim_done"] = True
        st.sidebar.success("✅ Semua skenario selesai!")

if btn_mc:
    if st.session_state["df"] is None:
        st.sidebar.error("⚠️ Upload dataset terlebih dahulu.")
    else:
        mc_progress = st.sidebar.progress(0, text="Memulai Monte Carlo…")

        def mc_callback(sc_idx, total_sc, it, n_it):
            pct  = ((sc_idx * n_it) + it + 1) / (total_sc * n_it)
            label = f"Skenario {sc_idx+1}/{total_sc} – Iterasi {it+1}/{n_it}"
            mc_progress.progress(min(pct, 1.0), text=label)

        df_mc = run_monte_carlo(st.session_state["df"], n_iterations=mc_iter, progress_callback=mc_callback)
        mc_progress.empty()
        st.session_state["df_mc"]   = df_mc
        st.session_state["mc_done"] = True
        st.sidebar.success("✅ Monte Carlo selesai!")


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="dashboard-title">💧 SimAntrian – Depot Air Minum</div>
<div class="dashboard-subtitle">
    Simulasi Sistem Antrian berbasis Agent-Based Modeling (ABM) &amp;
    Analisis Perilaku Pelanggan | Pemodelan &amp; Simulasi – UMM
</div>
""", unsafe_allow_html=True)

# Status dataset
if st.session_state["df"] is not None:
    fn  = st.session_state["file_name"]
    n   = len(st.session_state["df"])
    st.markdown(
        f'<span class="badge badge-blue">📄 {fn}</span> &nbsp;'
        f'<span class="badge badge-green">✅ {n} pelanggan</span>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<span class="badge badge-red">⚠️ Belum ada dataset – Upload CSV di sidebar</span>',
        unsafe_allow_html=True,
    )

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TABS UTAMA
# ═══════════════════════════════════════════════════════════════════════════════
tab_data, tab_sim, tab_viz, tab_mc, tab_insight = st.tabs([
    "📊 Dataset",
    "🔬 Simulasi",
    "📈 Visualisasi",
    "🎲 Monte Carlo",
    "💡 Insight",
])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1: DATASET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_data:
    if st.session_state["df"] is None:
        st.info("📂 Upload dataset CSV di **sidebar kiri** untuk memulai.")
        st.markdown("""
        **Format dataset yang diperlukan:**

        | pelanggan | kedatangan | layanan | sabar |
        |-----------|-----------|---------|-------|
        | P001      | 0         | 8       | 12    |
        | P002      | 3         | 6       | 10    |
        | P003      | 7         | 9       | 15    |

        - `pelanggan` : ID unik pelanggan  
        - `kedatangan`: waktu kedatangan (angka, urutan naik)  
        - `layanan`   : durasi layanan yang dibutuhkan  
        - `sabar`     : batas maksimal waktu tunggu pelanggan  
        """)
    else:
        df = st.session_state["df"]
        stats = dataset_stats(df)

        # KPI dataset
        st.markdown("#### Ringkasan Dataset")
        d_cols = st.columns(5)
        kpi_items = [
            ("👥", "Total Pelanggan",    stats["n_pelanggan"],   ""),
            ("⏱️", "Avg Kedatangan",     stats["avg_kedatangan"],""),
            ("🔧", "Avg Layanan",        stats["avg_layanan"],   ""),
            ("😤", "Avg Batas Sabar",    stats["avg_sabar"],     ""),
            ("📏", "Std Dev Layanan",    stats["std_layanan"],   ""),
        ]
        for col, (icon, label, val, delta) in zip(d_cols, kpi_items):
            col.metric(label=f"{icon} {label}", value=val)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        col_prev, col_stat = st.columns([3, 2])
        with col_prev:
            st.markdown("#### Preview Data")
            rows_to_show = st.slider("Tampilkan baris", 5, min(100, len(df)), 10)
            st.dataframe(df.head(rows_to_show), use_container_width=True, height=320)

        with col_stat:
            st.markdown("#### Statistik Deskriptif")
            desc = df[["kedatangan", "layanan", "sabar"]].describe().round(2)
            st.dataframe(desc, use_container_width=True)

        # Insight dataset
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("#### Insight Dataset")
        for ins in generate_dataset_insights(df):
            st.markdown(f"""
            <div class="insight-card {ins['type']}">
                <div class="insight-icon">{ins['icon']}</div>
                <div>
                    <div class="insight-title">{ins['title']}</div>
                    <div class="insight-detail">{ins['detail']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Download tombol
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Dataset (CSV)",
            data=csv_bytes,
            file_name="dataset_aktif.csv",
            mime="text/csv",
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2: SIMULASI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_sim:
    if not st.session_state["sim_done"] or not st.session_state["results"]:
        st.info("▶ Tekan **Simulasi** atau **Semua** di sidebar untuk menjalankan simulasi.")
    else:
        results = st.session_state["results"]
        df_sum  = results_to_dataframe(results)

        # Pilih skenario aktif
        st.markdown("#### Pilih Skenario Aktif")
        sel_key = st.selectbox(
            "Skenario",
            options=list(results.keys()),
            format_func=format_scenario_label,
            index=0,
        )
        st.session_state["active_scenario"] = sel_key
        active_data = results[sel_key]
        s = sim_summary(active_data)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # KPI Cards
        st.markdown("#### KPI Simulasi")
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        c1.metric("👥 Total Datang",   s["datang"])
        c2.metric("✅ Dilayani",        s["dilayani"])
        c3.metric("🚪 Pergi",          s["pergi"])
        c4.metric("⏱️ Avg Wait",       f"{s['avg_wait']:.2f}")
        c5.metric("⏱️ Max Wait",       f"{s['max_wait']:.2f}")
        c6.metric("😰 Avg Anxiety",    f"{s['avg_anxiety']:.3f}")
        c7.metric("😰 Max Anxiety",    f"{s['max_anxiety']:.3f}")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # Pie state agen
        col_pie, col_agents = st.columns([1, 2])
        with col_pie:
            st.plotly_chart(
                fig_agent_state_pie(active_data, format_scenario_label(sel_key)),
                use_container_width=True,
            )

        with col_agents:
            agent_logs = active_data.get("agent_logs", [])
            if agent_logs:
                st.markdown("#### Log Agen (10 Terakhir)")
                df_log = pd.DataFrame(agent_logs).tail(10)
                df_log["waktu_tunggu"] = df_log["waktu_tunggu"].round(2)
                df_log["anxiety_max"]  = df_log["anxiety_max"].round(3)
                st.dataframe(df_log, use_container_width=True)

        # Tabel ringkasan semua skenario
        if len(results) > 1:
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.markdown("#### Ringkasan Semua Skenario")
            df_show = df_sum[["label", "datang", "dilayani", "pergi", "avg_wait", "avg_anxiety"]].copy()
            df_show.columns = ["Skenario", "Datang", "Dilayani", "Pergi", "Avg Wait", "Avg Anxiety"]
            st.dataframe(df_show, use_container_width=True)

            csv_exp = df_sum.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Export Hasil Simulasi (CSV)",
                data=csv_exp,
                file_name="hasil_simulasi.csv",
                mime="text/csv",
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3: VISUALISASI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_viz:
    if not st.session_state["sim_done"] or not st.session_state["results"]:
        st.info("▶ Jalankan simulasi terlebih dahulu untuk melihat visualisasi.")
    else:
        results = st.session_state["results"]
        all_keys = list(results.keys())

        # Filter skenario
        sel_viz = st.multiselect(
            "Pilih skenario yang ditampilkan:",
            options=all_keys,
            default=all_keys[:min(4, len(all_keys))],
)
        if not sel_viz:
            sel_viz = all_keys

        vtab1, vtab2, vtab3, vtab4 = st.tabs([
            "📉 Kecemasan", "⏱️ Waktu Tunggu", "📦 Boxplot", "🔗 Komparasi"
        ])

        with vtab1:
            st.plotly_chart(fig_anxiety_line(results, sel_viz), use_container_width=True)
            st.plotly_chart(fig_anxiety_histogram(results, sel_viz), use_container_width=True)

        with vtab2:
            st.plotly_chart(fig_waiting_line(results, sel_viz), use_container_width=True)
            st.plotly_chart(fig_waiting_histogram(results, sel_viz), use_container_width=True)

        with vtab3:
            c_box1, c_box2 = st.columns(2)
            with c_box1:
                st.plotly_chart(fig_anxiety_boxplot(results), use_container_width=True)
            with c_box2:
                st.plotly_chart(fig_waiting_boxplot(results), use_container_width=True)

        with vtab4:
            st.plotly_chart(fig_comparison_bar(results), use_container_width=True)
            st.plotly_chart(fig_anxiety_vs_wait(results, sel_viz), use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4: MONTE CARLO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_mc:
    if not st.session_state["mc_done"] or st.session_state["df_mc"] is None:
        st.info("🎲 Tekan **Jalankan Monte Carlo** di sidebar untuk memulai pengujian.")
    else:
        df_mc = st.session_state["df_mc"]

        st.markdown("#### Hasil Monte Carlo – Semua Skenario")

        # KPI global
        mc_cols = st.columns(4)
        mc_cols[0].metric("Skenario Diuji",     len(df_mc))
        mc_cols[1].metric("Avg Wait Terbaik",   f"{df_mc['avg_wait_mean'].min():.2f}")
        mc_cols[2].metric("Pergi Terendah",     f"{df_mc['pergi_mean'].min():.1f}")
        mc_cols[3].metric("Anxiety Terendah",   f"{df_mc['avg_anxiety_mean'].min():.3f}")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # Grafik Monte Carlo
        fig_mc_wait, fig_mc_pergi = fig_monte_carlo(df_mc)
        col_mca, col_mcb = st.columns(2)
        with col_mca:
            st.plotly_chart(fig_mc_wait,  use_container_width=True)
        with col_mcb:
            st.plotly_chart(fig_mc_pergi, use_container_width=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # Tabel hasil lengkap
        with st.expander("📋 Tabel Lengkap Hasil Monte Carlo", expanded=True):
            df_mc_show = df_mc.copy()
            df_mc_show = df_mc_show.round(4)
            st.dataframe(df_mc_show, use_container_width=True)
            mc_csv = df_mc_show.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Export Monte Carlo (CSV)",
                data=mc_csv,
                file_name="monte_carlo_results.csv",
                mime="text/csv",
            )

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # Uji T
        with st.expander("🔬 Uji t – Perbandingan Dua Skenario", expanded=False):
            st.markdown("Bandingkan rata-rata waktu tunggu dua skenario menggunakan uji t independen (100 iterasi).")
            tc1, tc2 = st.columns(2)
            keys_all = scenario_keys_all()
            with tc1:
                sc_a = st.selectbox("Skenario A", keys_all, index=0, format_func=format_scenario_label, key="ta")
            with tc2:
                sc_b = st.selectbox("Skenario B", keys_all, index=4, format_func=format_scenario_label, key="tb")

            if st.button("▶ Jalankan Uji t") and st.session_state["df"] is not None:
                with st.spinner("Menghitung uji t…"):
                    parts_a = sc_a.split("_"); ma, ca = int(parts_a[0]), parts_a[2]
                    parts_b = sc_b.split("_"); mb, cb = int(parts_b[0]), parts_b[2]
                    ttest = ttest_two_scenarios(
                        st.session_state["df"],
                        (ma, ca), (mb, cb),
                        n_iterations=100,
                    )
                t_c1, t_c2, t_c3 = st.columns(3)
                t_c1.metric("t-statistik", ttest["t_stat"])
                t_c2.metric("p-value",     ttest["p_value"])
                t_c3.metric("Interpretasi", ttest["interpretation"])
                st.info(
                    f"Mean {format_scenario_label(sc_a)}: **{ttest['mean_a']:.4f}** | "
                    f"Mean {format_scenario_label(sc_b)}: **{ttest['mean_b']:.4f}**"
                )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 5: INSIGHT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_insight:
    if not st.session_state["sim_done"] or not st.session_state["results"]:
        st.info("💡 Jalankan simulasi untuk melihat insight otomatis.")
    else:
        results = st.session_state["results"]
        df_mc   = st.session_state.get("df_mc")

        st.markdown("#### Insight Otomatis Berbasis Simulasi")
        st.markdown("Sistem secara otomatis menganalisis hasil simulasi dan menghasilkan temuan berikut:")
        st.markdown("")

        insights = generate_insights(results, df_mc)
        for ins in insights:
            st.markdown(f"""
            <div class="insight-card {ins['type']}">
                <div class="insight-icon">{ins['icon']}</div>
                <div>
                    <div class="insight-title">{ins['title']}</div>
                    <div class="insight-detail">{ins['detail']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Tabel perbandingan ringkas
        if len(results) > 1:
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.markdown("#### Pivot: Pengaruh Mesin × Coping")
            df_sum = results_to_dataframe(results)

            parts  = df_sum["scenario"].str.split("_", expand=True)
            df_sum["mesin_label"]  = parts[0] + " Mesin"
            df_sum["coping_label"] = parts[2].map(COPING_ID)

            c_pivot1, c_pivot2 = st.columns(2)
            with c_pivot1:
                st.markdown("**Rata-rata Waktu Tunggu**")
                pivot_w = df_sum.pivot(index="mesin_label", columns="coping_label", values="avg_wait").round(3)
                st.dataframe(pivot_w, use_container_width=True)
            with c_pivot2:
                st.markdown("**Jumlah Pelanggan Pergi**")
                pivot_p = df_sum.pivot(index="mesin_label", columns="coping_label", values="pergi")
                st.dataframe(pivot_p, use_container_width=True)


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:rgba(99,102,241,0.15); margin:2rem 0 1rem;">
<div style="text-align:center; color:#475569; font-size:0.78rem; padding-bottom:1rem;">
    💧 <strong style="color:#6366F1;">SimAntrian</strong> &nbsp;|&nbsp;
    Pemodelan &amp; Simulasi – Universitas Muhammadiyah Malang &nbsp;|&nbsp;
    Dibangun dengan Python · Streamlit · SimPy · Plotly
</div>
""", unsafe_allow_html=True)
