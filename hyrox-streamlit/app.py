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

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; height: 0; }
.stDeployButton { display: none !important; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 100%; }

.stApp { background-color: #0d0d1a; }

.metric-card {
    background: linear-gradient(135deg, #12122a 0%, #1a1a38 100%);
    border-radius: 16px;
    padding: 24px 20px;
    box-shadow: 0 4px 24px rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.12);
    text-align: center;
    min-height: 136px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-bottom: 8px;
}
.metric-label {
    color: rgba(255,255,255,0.5);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.metric-value {
    font-size: 34px;
    font-weight: 800;
    color: #00E5FF;
    line-height: 1.1;
    margin-bottom: 6px;
}
.metric-value.pink  { color: #FF007A; }
.metric-value.green { color: #00E676; }
.metric-sub {
    font-size: 11px;
    color: rgba(255,255,255,0.35);
    letter-spacing: 0.04em;
}

.section-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.8);
    border-left: 3px solid #00E5FF;
    padding-left: 12px;
    margin: 32px 0 16px;
}

/* data_editor dark override */
.stDataFrame, [data-testid="stDataEditorContainer"] {
    background: transparent !important;
}
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
        (now, week_label, row["檢核項目"], row["我的回饋"], row["隊友回饋"])
        for _, row in df.iterrows()
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

# ── Simulated data (COROS / Strava mock) ─────────────────────────────────────
random.seed(7)
today = datetime.today()
dates = [(today - timedelta(days=i)).strftime("%m/%d") for i in range(6, -1, -1)]

df_sim = pd.DataFrame({
    "日期":               dates,
    "我的訓練負荷":       [random.randint(42, 92) for _ in range(7)],
    "隊友訓練負荷":       [random.randint(38, 88) for _ in range(7)],
    "我的配速 (min/km)":  [round(random.uniform(5.7, 7.3), 2) for _ in range(7)],
    "隊友配速 (min/km)":  [round(random.uniform(6.1, 7.9), 2) for _ in range(7)],
})

# ── Common chart layout ───────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.65)", size=12),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="rgba(255,255,255,0.4)")),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False,
               tickfont=dict(color="rgba(255,255,255,0.4)")),
    legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1,
                font=dict(size=11)),
    margin=dict(l=4, r=4, t=40, b=4),
    hovermode="x unified",
)

# ────────────────────────────────────────────────────────────────────────────
# PAGE LAYOUT
# ────────────────────────────────────────────────────────────────────────────

st.markdown("## HYROX 雙人備賽戰情中心")
st.markdown(
    '<p style="color:rgba(255,255,255,0.35);margin-top:-12px;margin-bottom:4px;font-size:13px;">'
    "Women's Doubles &nbsp;·&nbsp; Race Day: 2027-03-13"
    "</p>",
    unsafe_allow_html=True,
)

# ── Module 1: Metric Cards ────────────────────────────────────────────────────
st.markdown('<div class="section-title">核心指標</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">我的 Zone 2 均速</div>
        <div class="metric-value">6:12</div>
        <div class="metric-sub">min/km &nbsp;·&nbsp; 本週均值 · COROS</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">隊友 Zone 2 均速</div>
        <div class="metric-value pink">6:48</div>
        <div class="metric-sub">min/km &nbsp;·&nbsp; 本週均值 · Strava</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Sled Push 達標</div>
        <div class="metric-value green">✓ 102 kg</div>
        <div class="metric-sub">女子雙人標準 &nbsp;·&nbsp; 已達標</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Wall Balls 達標</div>
        <div class="metric-value pink">✗ 58 / 75</div>
        <div class="metric-sub">4 kg &nbsp;·&nbsp; 目標 75 下未達</div>
    </div>
    """, unsafe_allow_html=True)

# ── Module 2: Charts ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">訓練負荷與配速趨勢（過去 7 天）</div>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    fig_load = go.Figure()
    for label, col, color in [
        ("我 (COROS)",    "我的訓練負荷",  "#00E5FF"),
        ("隊友 (Strava)", "隊友訓練負荷",  "#FF007A"),
    ]:
        fig_load.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=label,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=7, color=color, line=dict(width=1.5, color="#0d0d1a")),
        ))
    fig_load.update_layout(**CHART_LAYOUT, title="訓練負荷 Training Load")
    st.plotly_chart(fig_load, use_container_width=True)

with col_r:
    fig_pace = go.Figure()
    for label, col, color, fill_color in [
        ("我 (COROS)",    "我的配速 (min/km)",  "#00E5FF", "rgba(0,229,255,0.07)"),
        ("隊友 (Strava)", "隊友配速 (min/km)",  "#FF007A", "rgba(255,0,122,0.07)"),
    ]:
        fig_pace.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=label,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=7, color=color, line=dict(width=1.5, color="#0d0d1a")),
            fill="tozeroy", fillcolor=fill_color,
        ))
    layout_pace = {**CHART_LAYOUT}
    layout_pace["yaxis"] = {**CHART_LAYOUT["yaxis"], "autorange": "reversed"}
    fig_pace.update_layout(**layout_pace, title="Zone 2 配速 (數值越小越快)")
    st.plotly_chart(fig_pace, use_container_width=True)

# ── Module 3: Weekly Review ───────────────────────────────────────────────────
st.markdown('<div class="section-title">每週雙向盤點</div>', unsafe_allow_html=True)

iso_week   = today.isocalendar()
week_label = f"{iso_week[0]}-W{iso_week[1]:02d}"

default_df = pd.DataFrame({
    "檢核項目": [
        "本週主觀疲勞 (RPE 1-10)",
        "Sled Push 重量達標情形",
        "下週合練重點",
    ],
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

col_btn, col_label = st.columns([1, 5])
with col_btn:
    save_clicked = st.button("儲存本週盤點", type="primary", use_container_width=True)

if save_clicked:
    save_review(edited_df, week_label)
    st.success(f"✓ 已儲存 {week_label} 的盤點記錄")

with st.expander("查看歷史盤點記錄"):
    history = load_history()
    if history.empty:
        st.caption("尚無記錄")
    else:
        st.dataframe(history, use_container_width=True, hide_index=True)
