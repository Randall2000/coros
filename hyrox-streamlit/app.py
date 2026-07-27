import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="HYROX 雙人備賽戰情中心",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS (Horizon UI Dark style) ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Hide Streamlit chrome */
#MainMenu, header[data-testid="stHeader"], footer,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
.stDeployButton { display: none !important; }

/* Global */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #0B1437 !important;
    font-family: 'Inter', system-ui, sans-serif;
}
.block-container {
    padding: 2rem 2rem 3rem !important;
    max-width: 100% !important;
}

/* ── Page header ── */
.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.page-title {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin: 0 0 4px;
}
.page-subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.4);
    font-weight: 400;
    margin: 0;
    letter-spacing: 0.02em;
}

/* ── Section label ── */
.section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45);
    margin: 2rem 0 1rem;
    padding-left: 10px;
    border-left: 2px solid #7551FF;
}

/* ── Metric card ── */
.kpi-card {
    background: linear-gradient(135deg, #111C44 0%, #1A2558 100%);
    border-radius: 20px;
    padding: 20px 22px 18px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 2px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
    min-height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-bottom: 4px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 20px 20px 0 0;
}
.kpi-card.purple::before { background: linear-gradient(90deg,#7551FF,#39B8FF); }
.kpi-card.cyan::before   { background: linear-gradient(90deg,#39B8FF,#00E5FF); }
.kpi-card.green::before  { background: linear-gradient(90deg,#01B574,#39DAAA); }
.kpi-card.red::before    { background: linear-gradient(90deg,#EE5D50,#FF9580); }

.kpi-icon {
    width: 40px; height: 40px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    margin-bottom: 12px;
    flex-shrink: 0;
}
.kpi-card.purple .kpi-icon { background: rgba(117,81,255,0.18); }
.kpi-card.cyan   .kpi-icon { background: rgba(57,184,255,0.18); }
.kpi-card.green  .kpi-icon { background: rgba(1,181,116,0.18); }
.kpi-card.red    .kpi-icon { background: rgba(238,93,80,0.18); }

.kpi-label {
    font-size: 12px;
    font-weight: 500;
    color: rgba(255,255,255,0.45);
    letter-spacing: 0.03em;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 8px;
}
.kpi-footer {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
}
.kpi-badge {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 11px;
}
.badge-green { background: rgba(1,181,116,0.15); color: #01B574; }
.badge-red   { background: rgba(238,93,80,0.15);  color: #EE5D50; }
.badge-gray  { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.4); }
.kpi-source  { color: rgba(255,255,255,0.3); font-size: 11px; }

/* ── Chart card ── */
.chart-card {
    background: #111C44;
    border-radius: 20px;
    padding: 22px 22px 8px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 2px 24px rgba(0,0,0,0.3);
    margin-bottom: 8px;
}
.chart-card-title {
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 2px;
    letter-spacing: -0.01em;
}
.chart-card-sub {
    font-size: 12px;
    color: rgba(255,255,255,0.35);
    margin-bottom: 12px;
}

/* ── data_editor override ── */
[data-testid="stDataEditorContainer"] iframe,
[data-testid="stDataFrame"] { border-radius: 16px !important; }
.stDataFrame { background: transparent !important; }

/* ── Button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7551FF, #39B8FF) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    padding: 0.55rem 1.4rem !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(117,81,255,0.35) !important;
    transition: opacity 0.15s !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #111C44 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 16px !important;
}
[data-testid="stExpander"] summary { color: rgba(255,255,255,0.6) !important; }
</style>
""", unsafe_allow_html=True)

# ── SQLite ────────────────────────────────────────────────────────────────────
DB_PATH = "hyrox_review.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weekly_review (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            saved_at         TEXT NOT NULL,
            week_label       TEXT NOT NULL,
            item             TEXT,
            my_feedback      TEXT,
            partner_feedback TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_review(df: pd.DataFrame, week_label: str):
    now = datetime.now().isoformat(timespec="seconds")
    rows = [
        (now, week_label, r["檢核項目"], r["我的回饋"], r["隊友回饋"])
        for _, r in df.iterrows()
    ]
    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT INTO weekly_review (saved_at, week_label, item, my_feedback, partner_feedback) VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()

def load_history(limit: int = 30) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        f"SELECT saved_at 儲存時間, week_label 週別, item 檢核項目, my_feedback 我的回饋, partner_feedback 隊友回饋 "
        f"FROM weekly_review ORDER BY saved_at DESC LIMIT {limit}",
        conn,
    )
    conn.close()
    return df

init_db()

# ── Simulated data ────────────────────────────────────────────────────────────
random.seed(7)
today = datetime.today()
dates = [(today - timedelta(days=i)).strftime("%m/%d") for i in range(6, -1, -1)]

df_sim = pd.DataFrame({
    "日期":              dates,
    "我的訓練負荷":      [random.randint(42, 92) for _ in range(7)],
    "隊友訓練負荷":      [random.randint(38, 88) for _ in range(7)],
    "我的配速":          [round(random.uniform(5.7, 7.3), 2) for _ in range(7)],
    "隊友配速":          [round(random.uniform(6.1, 7.9), 2) for _ in range(7)],
})

# ── Chart shared layout ───────────────────────────────────────────────────────
def chart_layout(title: str, yaxis_reversed: bool = False) -> dict:
    base = dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui", color="rgba(255,255,255,0.5)", size=11),
        title=dict(text=title, font=dict(size=14, color="rgba(255,255,255,0.75)", weight=600), x=0, xanchor="left"),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(color="rgba(255,255,255,0.35)", size=10),
            linecolor="rgba(255,255,255,0.06)",
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False,
            tickfont=dict(color="rgba(255,255,255,0.35)", size=10),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1,
            font=dict(size=11, color="rgba(255,255,255,0.55)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=0, r=0, t=44, b=0),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1A2558", bordercolor="rgba(255,255,255,0.1)",
            font=dict(color="white", size=12),
        ),
    )
    if yaxis_reversed:
        base["yaxis"]["autorange"] = "reversed"
    return base

# ────────────────────────────────────────────────────────────────────────────
# LAYOUT
# ────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
  <p class="page-title">HYROX 雙人備賽戰情中心</p>
  <p class="page-subtitle">Women's Doubles &nbsp;·&nbsp; Race Day: 2027-03-13 &nbsp;·&nbsp; 距今 {days} 天</p>
</div>
""".format(days=(datetime(2027, 3, 13) - today).days), unsafe_allow_html=True)

# ── Module 1: KPI Cards ───────────────────────────────────────────────────────
st.markdown('<div class="section-label">核心指標 · Today</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="kpi-card purple">
      <div>
        <div class="kpi-icon">🏃</div>
        <div class="kpi-label">我的 Zone 2 均速</div>
        <div class="kpi-value">6:12</div>
      </div>
      <div class="kpi-footer">
        <span class="kpi-badge badge-green">▲ +0:08</span>
        <span class="kpi-source">vs 上週 · COROS</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="kpi-card cyan">
      <div>
        <div class="kpi-icon">🤝</div>
        <div class="kpi-label">隊友 Zone 2 均速</div>
        <div class="kpi-value">6:48</div>
      </div>
      <div class="kpi-footer">
        <span class="kpi-badge badge-red">▼ -0:12</span>
        <span class="kpi-source">vs 上週 · Strava</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="kpi-card green">
      <div>
        <div class="kpi-icon">🛷</div>
        <div class="kpi-label">Sled Push 達標</div>
        <div class="kpi-value">102 kg</div>
      </div>
      <div class="kpi-footer">
        <span class="kpi-badge badge-green">✓ 達標</span>
        <span class="kpi-source">女子雙人標準</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="kpi-card red">
      <div>
        <div class="kpi-icon">🏐</div>
        <div class="kpi-label">Wall Balls 完成率</div>
        <div class="kpi-value">58 / 75</div>
      </div>
      <div class="kpi-footer">
        <span class="kpi-badge badge-red">✗ 未達標</span>
        <span class="kpi-source">4 kg · 差 17 下</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Module 2: Charts ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">訓練數據趨勢 · 近 7 天</div>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    st.markdown('<div class="chart-card"><div class="chart-card-title">訓練負荷</div><div class="chart-card-sub">Training Load · COROS vs Strava</div>', unsafe_allow_html=True)
    fig_load = go.Figure()
    for label, col, color, fill in [
        ("我 (COROS)",    "我的訓練負荷", "#7551FF", "rgba(117,81,255,0.12)"),
        ("隊友 (Strava)", "隊友訓練負荷", "#39B8FF", "rgba(57,184,255,0.08)"),
    ]:
        fig_load.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=label,
            mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.7),
            marker=dict(size=6, color=color, line=dict(width=2, color="#111C44")),
            fill="tozeroy", fillcolor=fill,
        ))
    fig_load.update_layout(**chart_layout(""))
    st.plotly_chart(fig_load, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="chart-card"><div class="chart-card-title">Zone 2 配速</div><div class="chart-card-sub">min/km · 數值越小越快</div>', unsafe_allow_html=True)
    fig_pace = go.Figure()
    for label, col, color, fill in [
        ("我 (COROS)",    "我的配速", "#01B574", "rgba(1,181,116,0.10)"),
        ("隊友 (Strava)", "隊友配速", "#FFB547", "rgba(255,181,71,0.08)"),
    ]:
        fig_pace.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=label,
            mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.7),
            marker=dict(size=6, color=color, line=dict(width=2, color="#111C44")),
            fill="tozeroy", fillcolor=fill,
        ))
    fig_pace.update_layout(**chart_layout("", yaxis_reversed=True))
    st.plotly_chart(fig_pace, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Module 3: Weekly Review ───────────────────────────────────────────────────
st.markdown('<div class="section-label">每週雙向盤點</div>', unsafe_allow_html=True)

iso = today.isocalendar()
week_label = f"{iso[0]}-W{iso[1]:02d}"

default_df = pd.DataFrame({
    "檢核項目": ["本週主觀疲勞 (RPE 1-10)", "Sled Push 重量達標情形", "下週合練重點"],
    "我的回饋":  ["", "", ""],
    "隊友回饋":  ["", "", ""],
})

edited_df = st.data_editor(
    default_df,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "檢核項目": st.column_config.TextColumn("檢核項目", disabled=True, width="medium"),
        "我的回饋": st.column_config.TextColumn("我的回饋 (COROS)", width="large"),
        "隊友回饋": st.column_config.TextColumn("隊友回饋 (Strava)", width="large"),
    },
)

col_btn, _ = st.columns([1, 5])
with col_btn:
    if st.button("儲存本週盤點", type="primary", use_container_width=True):
        save_review(edited_df, week_label)
        st.success(f"✓ {week_label} 已儲存到 hyrox_review.db")

with st.expander("查看歷史盤點記錄"):
    history = load_history()
    if history.empty:
        st.caption("尚無記錄")
    else:
        st.dataframe(history, use_container_width=True, hide_index=True)
