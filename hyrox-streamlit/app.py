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

# ── CSS — Material Design 3 Dark Data Visualization ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400;500&display=swap');

/* ── Reset Streamlit ── */
#MainMenu, header[data-testid="stHeader"], footer,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="manage-app-button"] { display: none !important; }
.stDeployButton { display: none !important; }

/* ── M3 Dark tokens ── */
:root {
  --md-sys-color-background:               #1C1B1F;
  --md-sys-color-surface:                  #1C1B1F;
  --md-sys-color-surface-container-low:    #1D1B20;
  --md-sys-color-surface-container:        #211F26;
  --md-sys-color-surface-container-high:   #2B2930;
  --md-sys-color-surface-container-highest:#36343B;
  --md-sys-color-on-surface:               #E6E1E5;
  --md-sys-color-on-surface-variant:       #CAC4D0;
  --md-sys-color-outline:                  rgba(202,196,208,0.16);
  --md-sys-color-outline-variant:          rgba(202,196,208,0.08);

  /* Chart palette — M3 extended tonal */
  --chart-a: #D0BCFF;   /* Primary purple */
  --chart-b: #80CBC4;   /* Teal */
  --chart-c: #EFB8C8;   /* Tertiary rose */
  --chart-d: #FFE082;   /* Amber */
  --chart-e: #90CAF9;   /* Blue */
  --chart-f: #A5D6A7;   /* Green */

  --good:    #4DB6AC;
  --warn:    #FFB74D;
  --error:   #EF9A9A;
  --info:    #90CAF9;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--md-sys-color-background) !important;
  font-family: 'Roboto', system-ui, sans-serif;
  color: var(--md-sys-color-on-surface);
  font-size: 14px; line-height: 1.5;
}
.block-container { padding: 28px 28px 64px !important; max-width: 100% !important; }

/* ── M3 Typography scale ── */
.md-display-sm  { font-size: 36px; font-weight: 400; line-height: 1.22; letter-spacing: 0; }
.md-headline-md { font-size: 28px; font-weight: 400; line-height: 1.29; letter-spacing: 0; }
.md-headline-sm { font-size: 24px; font-weight: 400; line-height: 1.33; letter-spacing: 0; }
.md-title-lg    { font-size: 22px; font-weight: 400; line-height: 1.27; letter-spacing: 0; }
.md-title-md    { font-size: 16px; font-weight: 500; line-height: 1.5;  letter-spacing: 0.15px; }
.md-title-sm    { font-size: 14px; font-weight: 500; line-height: 1.43; letter-spacing: 0.1px; }
.md-label-lg    { font-size: 14px; font-weight: 500; line-height: 1.43; letter-spacing: 0.1px; }
.md-label-md    { font-size: 12px; font-weight: 500; line-height: 1.33; letter-spacing: 0.5px; }
.md-label-sm    { font-size: 11px; font-weight: 500; line-height: 1.45; letter-spacing: 0.5px; }
.md-body-md     { font-size: 14px; font-weight: 400; line-height: 1.43; letter-spacing: 0.25px; }
.md-body-sm     { font-size: 12px; font-weight: 400; line-height: 1.33; letter-spacing: 0.4px; }

/* ── Page header ── */
.page-header {
  padding-bottom: 20px;
  border-bottom: 1px solid var(--md-sys-color-outline);
  margin-bottom: 28px;
}
.page-title {
  font-size: 22px; font-weight: 400;
  color: var(--md-sys-color-on-surface);
  letter-spacing: 0; margin: 0 0 8px;
}
.page-meta {
  display: flex; align-items: center; gap: 8px;
  flex-wrap: wrap;
}
.md-chip {
  display: inline-flex; align-items: center; gap: 4px;
  height: 32px; padding: 0 12px;
  border: 1px solid var(--md-sys-color-outline);
  border-radius: 8px;
  font-size: 14px; font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  background: transparent;
  white-space: nowrap;
}
.md-chip-filled {
  background: rgba(208,188,255,0.12);
  border-color: rgba(208,188,255,0.24);
  color: #D0BCFF;
}

/* ── Section header ── */
.sec-header {
  margin: 28px 0 16px;
  display: flex; align-items: baseline; gap: 12px;
}
.sec-title {
  font-size: 16px; font-weight: 500;
  color: var(--md-sys-color-on-surface);
  letter-spacing: 0.15px;
}
.sec-sub {
  font-size: 12px; font-weight: 400;
  color: var(--md-sys-color-on-surface-variant);
  letter-spacing: 0.4px;
}

/* ── M3 card — filled container ── */
.md-card {
  background: var(--md-sys-color-surface-container);
  border-radius: 12px;
  border: 1px solid var(--md-sys-color-outline-variant);
  overflow: hidden;
  margin-bottom: 4px;
}
.md-card-lg { background: var(--md-sys-color-surface-container-high); border-radius: 16px; }

/* ── Metric tile ── */
.metric-tile {
  background: var(--md-sys-color-surface-container);
  border-radius: 12px;
  border: 1px solid var(--md-sys-color-outline-variant);
  padding: 16px 20px 14px;
  position: relative;
  overflow: hidden;
  min-height: 112px;
  display: flex; flex-direction: column; gap: 10px;
}
.metric-tile-top {
  display: flex; align-items: center; justify-content: space-between;
}
.metric-icon {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
}
.metric-category {
  font-size: 11px; font-weight: 500;
  letter-spacing: 0.5px; text-transform: uppercase;
  color: var(--md-sys-color-on-surface-variant);
}
.metric-number {
  font-family: 'Roboto Mono', monospace;
  font-size: 34px; font-weight: 400;
  color: var(--md-sys-color-on-surface);
  letter-spacing: -0.5px; line-height: 1;
  margin: 0;
}
.metric-foot {
  display: flex; align-items: center; gap: 8px;
  margin-top: 2px;
}
.state-badge {
  font-size: 11px; font-weight: 500; letter-spacing: 0.5px;
  padding: 2px 8px; border-radius: 4px;
  display: inline-flex; align-items: center; gap: 4px;
}
.state-ok   { background: rgba(77,182,172,0.14); color: #4DB6AC; }
.state-med  { background: rgba(255,183,77,0.14); color: #FFB74D; }
.state-bad  { background: rgba(239,154,154,0.14);color: #EF9A9A; }
.state-info { background: rgba(144,202,249,0.14);color: #90CAF9; }
.metric-ctx {
  font-size: 11px; color: var(--md-sys-color-on-surface-variant);
  opacity: 0.7;
}

/* ── Activity list ── */
.act-table { width: 100%; border-collapse: collapse; }
.act-table th {
  font-size: 11px; font-weight: 500;
  letter-spacing: 0.5px; text-transform: uppercase;
  color: var(--md-sys-color-on-surface-variant);
  padding: 0 16px 12px;
  text-align: left;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}
.act-table th:first-child { padding-left: 20px; }
.act-table td {
  font-size: 14px; font-weight: 400;
  color: var(--md-sys-color-on-surface);
  padding: 12px 16px;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  vertical-align: middle;
  font-variant-numeric: tabular-nums;
}
.act-table td:first-child { padding-left: 20px; }
.act-table tr:last-child td { border-bottom: none; }
.act-label {
  display: inline-flex; align-items: center;
  font-size: 11px; font-weight: 500; letter-spacing: 0.5px;
  padding: 2px 8px; border-radius: 4px;
}
.act-label-str  { background: rgba(208,188,255,0.12); color: #D0BCFF; }
.act-label-run  { background: rgba(128,203,196,0.12); color: #80CBC4; }
.act-label-other{ background: rgba(202,196,208,0.10); color: #CAC4D0; }

/* ── Chart wrapper ── */
.chart-card {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  padding: 20px 20px 6px;
}
.chart-title {
  font-size: 14px; font-weight: 500;
  color: var(--md-sys-color-on-surface);
  letter-spacing: 0.1px; margin-bottom: 2px;
}
.chart-sub {
  font-size: 12px; font-weight: 400;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 10px;
}

/* ── Divider card ── */
.divider-card {
  background: var(--md-sys-color-surface-container);
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: 12px;
  padding: 16px 20px;
  display: flex; align-items: center; gap: 16px;
  min-height: 76px;
}
.divider-icon {
  width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}

/* ── Streamlit overrides ── */
[data-testid="stExpander"] {
  background: var(--md-sys-color-surface-container) !important;
  border: 1px solid var(--md-sys-color-outline-variant) !important;
  border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: var(--md-sys-color-on-surface-variant) !important; }
.stButton > button[kind="primary"] {
  background: #D0BCFF !important; color: #381E72 !important;
  border: none !important; border-radius: 20px !important;
  font-weight: 500 !important; font-size: 14px !important;
  letter-spacing: 0.1px !important; padding: 0 24px !important;
  height: 40px !important; transition: opacity 0.15s !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }
</style>
""", unsafe_allow_html=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
_here = Path(__file__).parent
_candidates = [
    _here.parent / "data",
    _here.parent / "hyrox-dashboard" / "data",
]
DATA = next((p for p in _candidates if p.exists()), _candidates[0])
DB   = _here / "hyrox_review.db"

# ── SQLite ────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS weekly_review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        saved_at TEXT NOT NULL, week_label TEXT NOT NULL,
        item TEXT, my_feedback TEXT, partner_feedback TEXT)""")
    conn.commit(); conn.close()

def save_review(df, week_label):
    now = datetime.now().isoformat(timespec="seconds")
    rows = [(now, week_label, r["檢核項目"], r["我的回饋"], r["隊友回饋"]) for _, r in df.iterrows()]
    conn = sqlite3.connect(DB)
    conn.executemany("INSERT INTO weekly_review (saved_at,week_label,item,my_feedback,partner_feedback) VALUES(?,?,?,?,?)", rows)
    conn.commit(); conn.close()

def load_history():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT saved_at 儲存時間,week_label 週別,item 檢核項目,my_feedback 我的回饋,partner_feedback 隊友回饋 FROM weekly_review ORDER BY saved_at DESC LIMIT 30", conn)
    conn.close(); return df

init_db()

# ── Data loaders ──────────────────────────────────────────────────────────────
def load_json(path):
    try: return json.loads(path.read_text())
    except: return {}

def parse_health(h):
    d = {"recovery":"—","recovery_level":"","sleep_score":"—","sleep_dur":"",
         "hr":"—","stress":"—","stress_label":"","updated":""}
    if not h: return d
    if m := re.search(r"Recovery[:\s]*(\d+)%", h.get("recovery",""), re.I):
        d["recovery"] = m.group(1) + "%"
    if m := re.search(r"Level[:\s]*(.+)", h.get("recovery",""), re.I):
        d["recovery_level"] = m.group(1).strip()
    if m := re.search(r"Sleep Score[:\s]*(\d+)", h.get("sleep",""), re.I):
        d["sleep_score"] = m.group(1)
    if m := re.search(r"Main Sleep[:\s]*([\dh min]+)", h.get("sleep",""), re.I):
        d["sleep_dur"] = m.group(1).strip()
    for line in h.get("hr","").splitlines():
        if m := re.search(r":\s*(\d+)\s*bpm", line, re.I):
            d["hr"] = m.group(1); break
    if m := re.search(r"Average Stress[:\s]*(\d+)\s*\(([^)]+)\)", h.get("stress",""), re.I):
        d["stress"] = m.group(1); d["stress_label"] = m.group(2).strip()
    if ts := h.get("updatedAt",""):
        try:
            dt = datetime.fromisoformat(ts.replace("Z","+00:00"))
            d["updated"] = dt.strftime("%m/%d %H:%M")
        except: pass
    return d

def parse_activities(a):
    text = a.get("activities","")
    records = []
    for block in re.split(r"\n\d+\.", text)[1:]:
        lines = block.strip().splitlines()
        if not lines: continue
        if not (m := re.match(r"(.+?)\s+[—-]\s+(\d{4}-\d{2}-\d{2})", lines[0].strip())): continue
        sport, date_str = m.group(1).strip(), m.group(2)
        dur = (dm.group(1) if (dm := re.search(r"Duration[:\s]*([\d:]+)", block, re.I)) else "—")
        hr  = (hm.group(1)+" bpm" if (hm := re.search(r"Avg HR[:\s]*(\d+)\s*bpm", block, re.I)) else "—")
        cal = (cm.group(1)+" kcal" if (cm := re.search(r"Calories[:\s]*(\d+)\s*kcal", block, re.I)) else "—")
        loc = (lm.group(1).strip() if (lm := re.search(r"Location[:\s]*(.+)", block, re.I)) else "")
        sl = sport.lower()
        tag = ("run" if any(w in sl for w in ["run","jog","cycling","swim","walk"])
               else "str" if any(w in sl for w in ["strength","weight"]) else "other")
        try: date_disp = datetime.strptime(date_str,"%Y-%m-%d").strftime("%m/%d")
        except: date_disp = date_str
        records.append({"date":date_disp,"name":loc or sport,"sport":sport,"dur":dur,"hr":hr,"cal":cal,"tag":tag})
    return records[:5]

# ── Simulated trend (partner = Strava stub) ───────────────────────────────────
random.seed(7)
today = datetime.today()
dates_7 = [(today-timedelta(days=i)).strftime("%m/%d") for i in range(6,-1,-1)]
df_sim = pd.DataFrame({
    "日期":     dates_7,
    "我的負荷": [random.randint(42,88) for _ in range(7)],
    "隊友負荷": [random.randint(38,82) for _ in range(7)],
    "我的配速": [round(random.uniform(5.8,7.2),2) for _ in range(7)],
    "隊友配速": [round(random.uniform(6.2,7.8),2) for _ in range(7)],
})

def chart_base(reverse_y=False):
    base = dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto,system-ui", color="#CAC4D0", size=11),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color="rgba(202,196,208,0.5)", size=10),
                   linecolor="rgba(202,196,208,0.1)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(202,196,208,0.08)", zeroline=False,
                   tickfont=dict(color="rgba(202,196,208,0.5)", size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="right", x=1,
                    font=dict(size=11, color="#CAC4D0"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=8, b=0),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#2B2930", bordercolor="rgba(202,196,208,0.2)",
                        font=dict(color="#E6E1E5", size=12)),
    )
    if reverse_y: base["yaxis"]["autorange"] = "reversed"
    return base

# ─────────────────────────────────────────────────────────────────────────────
# Load
# ─────────────────────────────────────────────────────────────────────────────
h_raw  = load_json(DATA / "health.json")
a_raw  = load_json(DATA / "activities.json")
health = parse_health(h_raw)
acts   = parse_activities(a_raw)

race_date  = datetime(2027, 3, 13)
days_left  = (race_date - today).days
iso        = today.isocalendar()
week_label = f"{iso[0]}-W{iso[1]:02d}"

# ─────────────────────────────────────────────────────────────────────────────
# PAGE
# ─────────────────────────────────────────────────────────────────────────────

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
  <p class="page-title">HYROX 雙人備賽戰情中心</p>
  <div class="page-meta">
    <span class="md-chip">Women's Doubles · 2027-03-13</span>
    <span class="md-chip md-chip-filled">距離比賽 {days_left} 天</span>
    {"<span class='md-chip'>已同步 " + health['updated'] + "</span>" if health['updated'] else ""}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Today's Health ────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header"><span class="sec-title">今日健康狀態</span><span class="sec-sub">COROS 自動同步</span></div>', unsafe_allow_html=True)

def classify(key, val):
    try: n = int(val.replace("%",""))
    except: return "state-info", "—"
    if key == "recovery":
        if n >= 75: return "state-ok", "優良"
        if n >= 50: return "state-med", "普通"
        return "state-bad", "偏低"
    if key == "sleep":
        if n >= 70: return "state-ok", "良好"
        if n >= 50: return "state-med", "普通"
        return "state-bad", "不足"
    if key == "hr":
        if n <= 55: return "state-ok", "低強度"
        if n <= 65: return "state-med", "正常"
        return "state-bad", "偏高"
    if key == "stress":
        if n <= 25: return "state-ok", "放鬆"
        if n <= 50: return "state-med", "輕度"
        return "state-bad", "高壓"
    return "state-info", "—"

r_cls, r_lbl = classify("recovery", health["recovery"])
s_cls, s_lbl = classify("sleep", health["sleep_score"])
h_cls, h_lbl = classify("hr", health["hr"])
st_cls, st_lbl = classify("stress", health["stress"])
if health["stress_label"]: st_lbl = health["stress_label"]

ICON_SVG = {
    "recovery": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "sleep":    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    "hr":       '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "stress":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
}

TILES = [
    ("recovery","恢復狀態","#D0BCFF","rgba(208,188,255,0.12)",health["recovery"],r_cls,r_lbl,health["recovery_level"] or "COROS"),
    ("sleep","睡眠評分","#80CBC4","rgba(128,203,196,0.12)",health["sleep_score"],s_cls,s_lbl,health["sleep_dur"] or "今晚"),
    ("hr","靜止心率","#90CAF9","rgba(144,202,249,0.12)",health["hr"]+" bpm" if health["hr"]!="—" else "—",h_cls,h_lbl,"今日"),
    ("stress","壓力指數","#FFE082","rgba(255,224,130,0.12)",health["stress"],st_cls,st_lbl,health["stress_label"] or "—"),
]

cols = st.columns(4)
for (key, label, color, iconbg, val, cls, badge, ctx), col in zip(TILES, cols):
    with col:
        st.markdown(f"""
        <div class="metric-tile">
          <div class="metric-tile-top">
            <span class="metric-category">{label}</span>
            <div class="metric-icon" style="background:{iconbg};color:{color}">{ICON_SVG[key]}</div>
          </div>
          <div>
            <div class="metric-number">{val}</div>
            <div class="metric-foot">
              <span class="state-badge {cls}">{badge}</span>
              <span class="metric-ctx">{ctx}</span>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

# ── Recent Activities ─────────────────────────────────────────────────────────
st.markdown('<div class="sec-header"><span class="sec-title">最近運動紀錄</span><span class="sec-sub">近 30 天 · 最多 5 筆 · 來自 COROS</span></div>', unsafe_allow_html=True)

if acts:
    label_map = {"str":"肌力","run":"有氧","other":"其他"}
    label_cls  = {"str":"act-label-str","run":"act-label-run","other":"act-label-other"}
    rows = ""
    for a in acts:
        sport_short = (a["sport"].replace("Custom Indoor Other","室內").replace("Strength","肌力訓練"))
        lbl = label_map.get(a["tag"],"—")
        lcls = label_cls.get(a["tag"],"act-label-other")
        rows += f"""<tr>
          <td style="color:#CAC4D0;font-size:12px">{a['date']}</td>
          <td><span style="color:#E6E1E5;font-weight:500">{a['name']}</span>
              <span style="color:#CAC4D0;font-size:12px;margin-left:6px">· {sport_short}</span></td>
          <td><span class="act-label {lcls}">{lbl}</span></td>
          <td>{a['dur']}</td><td>{a['hr']}</td>
          <td style="color:#CAC4D0">{a['cal']}</td></tr>"""
    st.markdown(f"""
    <div class="md-card">
    <table class="act-table">
      <thead><tr><th>日期</th><th>項目</th><th>類型</th><th>時長</th><th>平均心率</th><th>消耗</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="md-card" style="padding:32px;text-align:center;color:#CAC4D0;font-size:14px;">
      尚無運動記錄 — 等待 GitHub Actions 同步 COROS 資料
    </div>""", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header"><span class="sec-title">訓練趨勢</span><span class="sec-sub">近 7 天 · 隊友數據為 Strava 模擬（待串接）</span></div>', unsafe_allow_html=True)

cl, cr = st.columns(2)

with cl:
    st.markdown('<div class="chart-card"><div class="chart-title">訓練負荷</div><div class="chart-sub">Training Load · COROS vs Strava</div>', unsafe_allow_html=True)
    fig = go.Figure()
    for name, col, color, fill in [
        ("我 (COROS)",   "我的負荷","#D0BCFF","rgba(208,188,255,0.09)"),
        ("隊友 (Strava)","隊友負荷","#80CBC4","rgba(128,203,196,0.07)"),
    ]:
        fig.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=name, mode="lines+markers",
            line=dict(color=color, width=2, shape="spline", smoothing=0.5),
            marker=dict(size=5, color=color, line=dict(width=1.5, color="#211F26")),
            fill="tozeroy", fillcolor=fill,
        ))
    fig.update_layout(**chart_base())
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with cr:
    st.markdown('<div class="chart-card"><div class="chart-title">Zone 2 配速</div><div class="chart-sub">min/km · 數值越小代表越快</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for name, col, color, fill in [
        ("我 (COROS)",   "我的配速","#EFB8C8","rgba(239,184,200,0.09)"),
        ("隊友 (Strava)","隊友配速","#FFE082","rgba(255,224,130,0.07)"),
    ]:
        fig2.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=name, mode="lines+markers",
            line=dict(color=color, width=2, shape="spline", smoothing=0.5),
            marker=dict(size=5, color=color, line=dict(width=1.5, color="#211F26")),
            fill="tozeroy", fillcolor=fill,
        ))
    fig2.update_layout(**chart_base(reverse_y=True))
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Equipment goals ───────────────────────────────────────────────────────────
st.markdown('<div class="sec-header"><span class="sec-title">器材達標狀態</span><span class="sec-sub">Women\'s Doubles 官方標準</span></div>', unsafe_allow_html=True)

g1, g2 = st.columns(2)
with g1:
    st.markdown("""
    <div class="divider-card">
      <div class="divider-icon" style="background:rgba(128,203,196,0.12);color:#80CBC4">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="8" width="20" height="8" rx="2"/><line x1="6" y1="8" x2="6" y2="4"/><line x1="18" y1="8" x2="18" y2="4"/><line x1="6" y1="16" x2="6" y2="20"/><line x1="18" y1="16" x2="18" y2="20"/></svg>
      </div>
      <div>
        <div style="font-size:11px;font-weight:500;letter-spacing:0.5px;text-transform:uppercase;color:#CAC4D0">Sled Push</div>
        <div style="font-size:24px;font-weight:400;font-family:'Roboto Mono',monospace;color:#E6E1E5;margin:2px 0">102 kg</div>
        <div style="display:flex;align-items:center;gap:8px">
          <span class="state-badge state-ok">✓ 達標</span>
          <span style="font-size:11px;color:#CAC4D0">女子雙人標準</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

with g2:
    st.markdown("""
    <div class="divider-card">
      <div class="divider-icon" style="background:rgba(239,154,154,0.12);color:#EF9A9A">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
      </div>
      <div>
        <div style="font-size:11px;font-weight:500;letter-spacing:0.5px;text-transform:uppercase;color:#CAC4D0">Wall Balls · 4 kg</div>
        <div style="font-size:24px;font-weight:400;font-family:'Roboto Mono',monospace;color:#E6E1E5;margin:2px 0">58 / 75</div>
        <div style="display:flex;align-items:center;gap:8px">
          <span class="state-badge state-bad">✗ 差 17 下</span>
          <span style="font-size:11px;color:#CAC4D0">目標 75 下</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Weekly review ─────────────────────────────────────────────────────────────
st.markdown('<div class="sec-header"><span class="sec-title">每週雙向盤點</span><span class="sec-sub">填寫後儲存到本地 SQLite</span></div>', unsafe_allow_html=True)

default_df = pd.DataFrame({
    "檢核項目": ["本週主觀疲勞 (RPE 1-10)","Sled Push 重量達標情形","下週合練重點"],
    "我的回饋": ["","",""],
    "隊友回饋": ["","",""],
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
    if hist.empty: st.caption("尚無記錄")
    else: st.dataframe(hist, use_container_width=True, hide_index=True)
