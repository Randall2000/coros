import re
import sqlite3
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import random

st.set_page_config(
    page_title="HYROX 雙人備賽戰情中心",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
# Streamlit Cloud: app is at hyrox-streamlit/app.py inside repo → parent.parent = repo root
# Local dev (standalone dir): data is in sibling hyrox-dashboard/data/
_here = Path(__file__).parent
_candidates = [
    _here.parent / "data",                        # in-repo (Streamlit Cloud)
    _here.parent / "hyrox-dashboard" / "data",   # local sibling repo
]
DATA = next((p for p in _candidates if p.exists()), _candidates[0])
DB   = _here / "hyrox_review.db"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500;600&display=swap');

/* ── reset Streamlit chrome ── */
#MainMenu, header[data-testid="stHeader"], footer,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="manage-app-button"] { display: none !important; }
.stDeployButton { display: none !important; }

/* ── global ── */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: #080b14 !important;
    font-family: 'Barlow', system-ui, sans-serif;
    color: #e2e8f0;
}
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 100% !important; }

/* ── page header ── */
.ph { margin-bottom: 2.5rem; }
.ph-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 28px; font-weight: 800;
    color: #fff; letter-spacing: -0.02em;
    margin: 0 0 6px;
}
.ph-meta {
    font-size: 13px; font-weight: 400;
    color: rgba(255,255,255,0.38);
    display: flex; align-items: center; gap: 12px;
}
.ph-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 12px; font-weight: 500;
    color: rgba(255,255,255,0.55);
}
.ph-countdown {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 14px; font-weight: 700;
    color: #7551FF;
}

/* ── section header ── */
.sh {
    margin: 2.5rem 0 1rem;
    display: flex; align-items: baseline; gap: 10px;
}
.sh-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 18px; font-weight: 700;
    color: #fff; letter-spacing: 0.01em;
}
.sh-sub {
    font-size: 12px; font-weight: 400;
    color: rgba(255,255,255,0.3);
}

/* ── KPI card ── */
.kpi {
    background: #101828;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 20px;
    display: flex; flex-direction: column; gap: 12px;
    min-height: 118px;
    position: relative; overflow: hidden;
}
.kpi-accent {
    position: absolute; top: 0; left: 0; right: 0;
    height: 3px; border-radius: 16px 16px 0 0;
}
.kpi-row { display: flex; align-items: center; justify-content: space-between; }
.kpi-icon {
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
}
.kpi-label {
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.09em; text-transform: uppercase;
    color: rgba(255,255,255,0.38);
}
.kpi-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 32px; font-weight: 800;
    color: #fff; letter-spacing: -0.02em; line-height: 1;
    margin: 2px 0 4px;
}
.kpi-foot { display: flex; align-items: center; gap: 8px; }
.badge {
    font-size: 11px; font-weight: 600;
    padding: 2px 9px; border-radius: 8px;
    display: inline-flex; align-items: center; gap: 3px;
}
.badge-ok  { background: rgba(1,181,116,0.14); color: #01B574; }
.badge-warn{ background: rgba(238,93,80,0.14);  color: #EE5D50; }
.badge-med { background: rgba(251,191,36,0.14); color: #FBBF24; }
.badge-info{ background: rgba(117,81,255,0.14); color: #9F7AEA; }
.kpi-ctx   { font-size: 11px; color: rgba(255,255,255,0.28); }

/* ── activity table ── */
.act-table { width: 100%; border-collapse: collapse; }
.act-table th {
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: rgba(255,255,255,0.3);
    padding: 0 0 10px; text-align: left;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.act-table td {
    font-size: 14px; font-weight: 400;
    color: rgba(255,255,255,0.75);
    padding: 11px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    vertical-align: middle;
}
.act-table td:first-child { font-weight: 600; color: #fff; }
.act-tag {
    display: inline-block;
    font-size: 11px; font-weight: 600;
    padding: 2px 8px; border-radius: 6px;
    background: rgba(117,81,255,0.15); color: #9F7AEA;
}
.act-tag.run  { background: rgba(1,181,116,0.13); color: #34D399; }
.act-tag.str  { background: rgba(251,191,36,0.12); color: #FBBF24; }
.act-tag.other{ background: rgba(148,163,184,0.1); color: #94A3B8; }
.no-data {
    font-size: 13px; color: rgba(255,255,255,0.25);
    padding: 20px 0; text-align: center;
}

/* ── chart card ── */
.cc {
    background: #101828;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 20px 20px 4px;
    margin-bottom: 4px;
}
.cc-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 16px; font-weight: 700; color: #fff;
    margin-bottom: 2px;
}
.cc-sub { font-size: 12px; color: rgba(255,255,255,0.3); margin-bottom: 8px; }

/* ── editor / expander ── */
[data-testid="stExpander"] {
    background: #101828 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
}
[data-testid="stExpander"] summary { color: rgba(255,255,255,0.5) !important; }

/* ── button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#7551FF,#39B8FF) !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'Barlow', sans-serif !important;
    font-weight: 600 !important; font-size: 14px !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(117,81,255,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ── SQLite ────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS weekly_review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        saved_at TEXT NOT NULL, week_label TEXT NOT NULL,
        item TEXT, my_feedback TEXT, partner_feedback TEXT
    )""")
    conn.commit(); conn.close()

def save_review(df, week_label):
    now = datetime.now().isoformat(timespec="seconds")
    rows = [(now, week_label, r["檢核項目"], r["我的回饋"], r["隊友回饋"]) for _, r in df.iterrows()]
    conn = sqlite3.connect(DB)
    conn.executemany("INSERT INTO weekly_review (saved_at,week_label,item,my_feedback,partner_feedback) VALUES(?,?,?,?,?)", rows)
    conn.commit(); conn.close()

def load_history():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT saved_at 儲存時間, week_label 週別, item 檢核項目, my_feedback 我的回饋, partner_feedback 隊友回饋 FROM weekly_review ORDER BY saved_at DESC LIMIT 30", conn)
    conn.close(); return df

init_db()

# ── Real data parsers ─────────────────────────────────────────────────────────
def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}

def parse_health(h: dict) -> dict:
    out = {"recovery": "—", "recovery_level": "", "sleep_score": "—",
           "sleep_dur": "", "hr": "—", "stress": "—", "stress_label": "",
           "updated": ""}
    if not h:
        return out

    r = h.get("recovery", "")
    m = re.search(r"Recovery[:\s]*(\d+)%", r, re.I)
    if m: out["recovery"] = m.group(1) + "%"
    ml = re.search(r"Level[:\s]*(.+)", r, re.I)
    if ml: out["recovery_level"] = ml.group(1).strip()

    s = h.get("sleep", "")
    ms = re.search(r"Sleep Score[:\s]*(\d+)", s, re.I)
    if ms: out["sleep_score"] = ms.group(1)
    md = re.search(r"Main Sleep[:\s]*([\dh min]+)", s, re.I)
    if md: out["sleep_dur"] = md.group(1).strip()

    hr_text = h.get("hr", "")
    for line in hr_text.splitlines():
        bm = re.search(r":\s*(\d+)\s*bpm", line, re.I)
        if bm:
            out["hr"] = bm.group(1)
            break

    st_text = h.get("stress", "")
    sm = re.search(r"Average Stress[:\s]*(\d+)\s*\(([^)]+)\)", st_text, re.I)
    if sm:
        out["stress"] = sm.group(1)
        out["stress_label"] = sm.group(2).strip()

    ts = h.get("updatedAt", "")
    if ts:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            out["updated"] = dt.strftime("%m/%d %H:%M")
        except Exception:
            pass
    return out

def parse_activities(a: dict) -> list[dict]:
    text = a.get("activities", "")
    records = []
    blocks = re.split(r"\n\d+\.", text)
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        header = lines[0].strip() if lines else ""
        m = re.match(r"(.+?)\s+[—-]\s+(\d{4}-\d{2}-\d{2})", header)
        if not m:
            continue
        sport = m.group(1).strip()
        date_str = m.group(2)

        # duration
        dur = "—"
        dm = re.search(r"Duration[:\s]*([\d:]+)", block, re.I)
        if dm: dur = dm.group(1)

        # avg HR
        hr = "—"
        hm = re.search(r"Avg HR[:\s]*(\d+)\s*bpm", block, re.I)
        if hm: hr = hm.group(1) + " bpm"

        # calories
        cal = "—"
        cm = re.search(r"Calories[:\s]*(\d+)\s*kcal", block, re.I)
        if cm: cal = cm.group(1) + " kcal"

        # location / name
        loc = ""
        lm = re.search(r"Location[:\s]*(.+)", block, re.I)
        if lm: loc = lm.group(1).strip()

        # sport type tag
        sport_lower = sport.lower()
        if any(w in sport_lower for w in ["run", "jog", "cycling", "swim", "walk"]):
            tag = "run"
        elif any(w in sport_lower for w in ["strength", "weight"]):
            tag = "str"
        else:
            tag = "other"

        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            date_disp = d.strftime("%m/%d")
        except Exception:
            date_disp = date_str

        display_name = loc if loc else sport
        records.append({"date": date_disp, "name": display_name,
                         "sport": sport, "dur": dur, "hr": hr,
                         "cal": cal, "tag": tag})
    return records[:5]

# ── Simulated trend data (partner = Strava, not yet integrated) ───────────────
random.seed(7)
today = datetime.today()
dates_7 = [(today - timedelta(days=i)).strftime("%m/%d") for i in range(6, -1, -1)]
df_sim = pd.DataFrame({
    "日期":       dates_7,
    "我的負荷":   [random.randint(42, 88) for _ in range(7)],
    "隊友負荷":   [random.randint(38, 82) for _ in range(7)],
    "我的配速":   [round(random.uniform(5.8, 7.2), 2) for _ in range(7)],
    "隊友配速":   [round(random.uniform(6.2, 7.8), 2) for _ in range(7)],
})

# ── Chart layout factory ──────────────────────────────────────────────────────
def clayout(reverse_y=False):
    base = dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Barlow, system-ui", color="rgba(255,255,255,0.4)", size=11),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color="rgba(255,255,255,0.3)", size=10),
                   linecolor="rgba(255,255,255,0.05)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.045)",
                   zeroline=False, tickfont=dict(color="rgba(255,255,255,0.3)", size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="right", x=1,
                    font=dict(size=11, color="rgba(255,255,255,0.5)"),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=8, b=0),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1a2540", bordercolor="rgba(255,255,255,0.08)",
                        font=dict(color="#fff", size=12)),
    )
    if reverse_y:
        base["yaxis"]["autorange"] = "reversed"
    return base

# ─────────────────────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────────────────────
h_raw  = load_json(DATA / "health.json")
a_raw  = load_json(DATA / "activities.json")
health = parse_health(h_raw)
acts   = parse_activities(a_raw)

race_date   = datetime(2027, 3, 13)
days_to_go  = (race_date - today).days
iso         = today.isocalendar()
week_label  = f"{iso[0]}-W{iso[1]:02d}"

# ─────────────────────────────────────────────────────────────────────────────
# PAGE
# ─────────────────────────────────────────────────────────────────────────────

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ph">
  <p class="ph-title">HYROX 雙人備賽戰情中心</p>
  <div class="ph-meta">
    <span class="ph-pill">Women's Doubles · 2027-03-13</span>
    <span class="ph-countdown">距離比賽 {days_to_go} 天</span>
    {"<span class='ph-pill'>更新 " + health['updated'] + "</span>" if health['updated'] else ""}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Section 1: Today's Health ────────────────────────────────────────────────
st.markdown('<div class="sh"><span class="sh-title">今日健康狀態</span><span class="sh-sub">來自 COROS · 每日自動同步</span></div>', unsafe_allow_html=True)

def recovery_badge(v):
    try:
        n = int(v.replace("%", ""))
        if n >= 75: return "badge-ok", "優良"
        if n >= 50: return "badge-med", "普通"
        return "badge-warn", "偏低"
    except Exception:
        return "badge-info", "—"

def sleep_badge(v):
    try:
        n = int(v)
        if n >= 70: return "badge-ok", "良好"
        if n >= 50: return "badge-med", "普通"
        return "badge-warn", "不足"
    except Exception:
        return "badge-info", "—"

def hr_badge(v):
    try:
        n = int(v)
        if n <= 55: return "badge-ok", "低強度"
        if n <= 65: return "badge-med", "正常"
        return "badge-warn", "偏高"
    except Exception:
        return "badge-info", "—"

def stress_badge(v, label):
    try:
        n = int(v)
        if n <= 25: return "badge-ok", label or "放鬆"
        if n <= 50: return "badge-med", label or "低度"
        return "badge-warn", label or "高壓"
    except Exception:
        return "badge-info", label or "—"

rb_cls, rb_lbl = recovery_badge(health["recovery"])
sb_cls, sb_lbl = sleep_badge(health["sleep_score"])
hb_cls, hb_lbl = hr_badge(health["hr"])
stb_cls, stb_lbl = stress_badge(health["stress"], health["stress_label"])

c1, c2, c3, c4 = st.columns(4)

CARDS = [
    (c1, "#7551FF,#39B8FF", "rgba(117,81,255,0.14)", "#9F7AEA",
     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
     "恢復狀態", health["recovery"], rb_cls, rb_lbl, health["recovery_level"] or "COROS 數據"),
    (c2, "#01B574,#39DAAA", "rgba(1,181,116,0.13)", "#34D399",
     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
     "睡眠評分", health["sleep_score"], sb_cls, sb_lbl, health["sleep_dur"] or "今晚"),
    (c3, "#3B82F6,#60A5FA", "rgba(59,130,246,0.13)", "#60A5FA",
     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
     "靜止心率", health["hr"] + (" bpm" if health["hr"] != "—" else ""), hb_cls, hb_lbl, "今日最新"),
    (c4, "#FBBF24,#F59E0B", "rgba(251,191,36,0.12)", "#FBBF24",
     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
     "壓力指數", health["stress"], stb_cls, stb_lbl, health["stress_label"] or "—"),
]

for col, grad, iconbg, iconcol, icon_svg, label, value, bcls, blbl, ctx in CARDS:
    with col:
        st.markdown(f"""
        <div class="kpi">
          <div class="kpi-accent" style="background:linear-gradient(90deg,{grad});"></div>
          <div class="kpi-row">
            <div class="kpi-label">{label}</div>
            <div class="kpi-icon" style="background:{iconbg};color:{iconcol};">{icon_svg}</div>
          </div>
          <div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">
              <span class="badge {bcls}">{blbl}</span>
              <span class="kpi-ctx">{ctx}</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Section 2: Recent Activities ─────────────────────────────────────────────
st.markdown('<div class="sh"><span class="sh-title">最近運動紀錄</span><span class="sh-sub">近 30 天 · 最多 5 筆</span></div>', unsafe_allow_html=True)

if acts:
    rows_html = ""
    for a in acts:
        tag_cls = a["tag"]
        sport_short = a["sport"].replace("Custom Indoor Other", "室內").replace("Strength", "肌力")
        type_label = {"run": "有氧", "str": "肌力", "other": "其他"}.get(tag_cls, "—")
        rows_html += f"""
        <tr>
          <td style="width:60px">{a['date']}</td>
          <td>{a['name']} <span style="color:rgba(255,255,255,0.3);font-size:12px">· {sport_short}</span></td>
          <td><span class="act-tag {tag_cls}">{type_label}</span></td>
          <td style="font-variant-numeric:tabular-nums">{a['dur']}</td>
          <td style="font-variant-numeric:tabular-nums">{a['hr']}</td>
          <td style="font-variant-numeric:tabular-nums;color:rgba(255,255,255,0.45)">{a['cal']}</td>
        </tr>"""
    st.markdown(f"""
    <table class="act-table">
      <thead><tr>
        <th>日期</th><th>項目</th><th>類型</th><th>時長</th><th>心率</th><th>消耗</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)
else:
    st.markdown('<div class="no-data">尚無運動記錄（data/activities.json 未同步）</div>', unsafe_allow_html=True)

# ── Section 3: Charts ─────────────────────────────────────────────────────────
st.markdown('<div class="sh"><span class="sh-title">訓練趨勢</span><span class="sh-sub">近 7 天模擬 · 待 Strava 串接後更新</span></div>', unsafe_allow_html=True)

cl, cr = st.columns(2)

with cl:
    st.markdown('<div class="cc"><div class="cc-title">訓練負荷</div><div class="cc-sub">Training Load · COROS vs Strava（模擬）</div>', unsafe_allow_html=True)
    fig = go.Figure()
    for name, col, color, fill in [
        ("我 (COROS)", "我的負荷", "#7551FF", "rgba(117,81,255,0.1)"),
        ("隊友 (Strava)", "隊友負荷", "#39B8FF", "rgba(57,184,255,0.08)"),
    ]:
        fig.add_trace(go.Scatter(x=df_sim["日期"], y=df_sim[col], name=name,
            mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.6),
            marker=dict(size=6, color=color, line=dict(width=2, color="#101828")),
            fill="tozeroy", fillcolor=fill))
    fig.update_layout(**clayout())
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with cr:
    st.markdown('<div class="cc"><div class="cc-title">Zone 2 配速</div><div class="cc-sub">min/km · 數值越小代表越快</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for name, col, color, fill in [
        ("我 (COROS)", "我的配速", "#01B574", "rgba(1,181,116,0.09)"),
        ("隊友 (Strava)", "隊友配速", "#FBBF24", "rgba(251,191,36,0.07)"),
    ]:
        fig2.add_trace(go.Scatter(x=df_sim["日期"], y=df_sim[col], name=name,
            mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.6),
            marker=dict(size=6, color=color, line=dict(width=2, color="#101828")),
            fill="tozeroy", fillcolor=fill))
    fig2.update_layout(**clayout(reverse_y=True))
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Section 4: Sled / Wall Balls status ──────────────────────────────────────
st.markdown('<div class="sh"><span class="sh-title">HYROX 特定器材達標</span><span class="sh-sub">Women\'s Doubles 標準</span></div>', unsafe_allow_html=True)

g1, g2 = st.columns(2)
with g1:
    st.markdown("""
    <div class="kpi" style="flex-direction:row;align-items:center;gap:20px;min-height:80px;">
      <div class="kpi-accent" style="background:linear-gradient(90deg,#01B574,#39DAAA);"></div>
      <div class="kpi-icon" style="background:rgba(1,181,116,0.13);color:#34D399;width:44px;height:44px;border-radius:12px;flex-shrink:0;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="8" width="20" height="8" rx="2"/><line x1="6" y1="8" x2="6" y2="4"/><line x1="18" y1="8" x2="18" y2="4"/><line x1="6" y1="16" x2="6" y2="20"/><line x1="18" y1="16" x2="18" y2="20"/></svg>
      </div>
      <div>
        <div class="kpi-label">Sled Push</div>
        <div class="kpi-value" style="font-size:26px">102 kg</div>
        <div class="kpi-foot"><span class="badge badge-ok">✓ 達標</span><span class="kpi-ctx">女子雙人標準</span></div>
      </div>
    </div>""", unsafe_allow_html=True)
with g2:
    st.markdown("""
    <div class="kpi" style="flex-direction:row;align-items:center;gap:20px;min-height:80px;">
      <div class="kpi-accent" style="background:linear-gradient(90deg,#EE5D50,#FF9580);"></div>
      <div class="kpi-icon" style="background:rgba(238,93,80,0.13);color:#EE5D50;width:44px;height:44px;border-radius:12px;flex-shrink:0;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
      </div>
      <div>
        <div class="kpi-label">Wall Balls · 4 kg</div>
        <div class="kpi-value" style="font-size:26px">58 / 75</div>
        <div class="kpi-foot"><span class="badge badge-warn">✗ 差 17 下</span><span class="kpi-ctx">目標 75 下</span></div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Section 5: Weekly Review ──────────────────────────────────────────────────
st.markdown('<div class="sh"><span class="sh-title">每週雙向盤點</span><span class="sh-sub">填完後儲存，記錄寫入本地 SQLite</span></div>', unsafe_allow_html=True)

default_df = pd.DataFrame({
    "檢核項目": ["本週主觀疲勞 (RPE 1-10)", "Sled Push 重量達標情形", "下週合練重點"],
    "我的回饋":  ["", "", ""],
    "隊友回饋":  ["", "", ""],
})
edited_df = st.data_editor(
    default_df, use_container_width=True, hide_index=True, num_rows="fixed",
    column_config={
        "檢核項目": st.column_config.TextColumn("檢核項目", disabled=True, width="medium"),
        "我的回饋": st.column_config.TextColumn("我的回饋 (COROS)", width="large"),
        "隊友回饋": st.column_config.TextColumn("隊友回饋 (Strava)", width="large"),
    },
)
cb, _ = st.columns([1, 5])
with cb:
    if st.button("儲存本週盤點", type="primary", use_container_width=True):
        save_review(edited_df, week_label)
        st.success(f"✓ {week_label} 已儲存")

with st.expander("查看歷史盤點記錄"):
    hist = load_history()
    if hist.empty:
        st.caption("尚無記錄")
    else:
        st.dataframe(hist, use_container_width=True, hide_index=True)
