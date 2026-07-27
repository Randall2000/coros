import re, sqlite3, json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import random

st.set_page_config(
    page_title="HYROX War Room · Randall & Zoe",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400;500&display=swap');

#MainMenu, header[data-testid="stHeader"], footer,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="manage-app-button"], .stDeployButton { display: none !important; }

:root {
  --bg:      #1C1B1F;
  --surf:    #211F26;
  --s-hi:    #2B2930;
  --s-top:   #36343B;
  --on:      #E6E1E5;
  --on-v:    #CAC4D0;
  --out:     rgba(202,196,208,0.16);
  --out-v:   rgba(202,196,208,0.08);
  --r:       #D0BCFF;
  --r-bg:    rgba(208,188,255,0.10);
  --r-bd:    rgba(208,188,255,0.22);
  --z:       #60A5FA;
  --z-bg:    rgba(96,165,250,0.10);
  --z-bd:    rgba(96,165,250,0.22);
  --ok:      #4DB6AC;
  --wrn:     #FFB74D;
  --err:     #EF9A9A;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'Roboto', system-ui, sans-serif;
  color: var(--on); font-size: 14px; line-height: 1.5;
}
.block-container { padding: 20px 24px 64px !important; max-width: 100% !important; }

/* PAGE HEADER */
.ph { padding-bottom: 14px; border-bottom: 1px solid var(--out); margin-bottom: 0; }
.ph-title { font-size: 20px; font-weight: 400; margin: 0 0 6px; }
.ph-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.chip { display: inline-flex; align-items: center; height: 26px; padding: 0 10px;
  border: 1px solid var(--out); border-radius: 6px;
  font-size: 12px; font-weight: 500; color: var(--on-v); }
.chip-r { background: var(--r-bg); border-color: var(--r-bd); color: var(--r); }
.sync-lbl { font-size: 11px; color: rgba(202,196,208,0.4); margin-left: auto; }

/* SECTION HEADER */
.sh { margin: 28px 0 14px; }
.sh-tag { font-size: 10px; font-weight: 500; letter-spacing: 1.5px;
  text-transform: uppercase; color: var(--on-v); margin-bottom: 3px; }
.sh-title { font-size: 20px; font-weight: 400; color: var(--on); margin: 0; }
.sh-sub { font-size: 12px; color: var(--on-v); margin-top: 2px; }

/* WAR ROOM */
.wr { background: var(--surf); border: 1px solid var(--out);
  border-radius: 16px; padding: 22px 24px 18px; }
.wr-standings { display: flex; align-items: stretch; gap: 12px; margin-bottom: 16px; }
.pc { flex: 1; border-radius: 12px; padding: 16px 18px;
  display: flex; flex-direction: column; gap: 6px; }
.pc-r { background: var(--r-bg); border: 1px solid var(--r-bd); }
.pc-z { background: var(--z-bg); border: 1px solid var(--z-bd); }
.pc-name { font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }
.pc-name-r { color: var(--r); }
.pc-name-z { color: var(--z); }
.pc-score { font-family: 'Roboto Mono', monospace;
  font-size: 42px; font-weight: 400; line-height: 1; letter-spacing: -1px; color: var(--on); }
.pc-unit { font-size: 14px; color: var(--on-v); }
.pc-sub { font-size: 11px; color: var(--on-v); }
.lp { align-self: center; padding: 10px 14px; border-radius: 24px;
  text-align: center; min-width: 100px; }
.lp-r { background: var(--r-bg); border: 1px solid var(--r-bd); }
.lp-z { background: var(--z-bg); border: 1px solid var(--z-bd); }
.lp-pts { font-family: 'Roboto Mono', monospace;
  font-size: 22px; font-weight: 400; line-height: 1; }
.lp-pts-r { color: var(--r); }
.lp-pts-z { color: var(--z); }
.lp-lbl { font-size: 10px; font-weight: 500; letter-spacing: 0.5px; color: var(--on-v); margin-top: 2px; }
.wr-pace { display: flex; gap: 10px; }
.wp { flex: 1; border-radius: 10px; background: var(--s-hi);
  border: 1px solid var(--out-v); padding: 12px 16px;
  display: flex; align-items: center; justify-content: space-between; }
.wp-lbl { font-size: 11px; color: var(--on-v); margin-bottom: 2px; }
.wp-val { font-family: 'Roboto Mono', monospace; font-size: 16px; color: var(--on); }
.dl { font-size: 11px; padding: 2px 7px; border-radius: 4px; font-weight: 500; }
.dl-r { background: var(--r-bg); color: var(--r); }
.dl-z { background: var(--z-bg); color: var(--z); }
.dl-n { background: rgba(202,196,208,0.08); color: var(--on-v); }

/* CHART CARD */
.cc { background: var(--surf); border: 1px solid var(--out-v);
  border-radius: 12px; padding: 16px 16px 6px; }
.cc-title { font-size: 14px; font-weight: 500; color: var(--on); margin-bottom: 2px; }
.cc-sub { font-size: 11px; color: var(--on-v); margin-bottom: 8px; }
.cc-stats { display: flex; padding-top: 6px; border-top: 1px solid var(--out-v); }
.cc-stat { flex: 1; padding: 8px 12px; border-right: 1px solid var(--out-v); }
.cc-stat:last-child { border-right: none; }
.cc-stat-val { font-family: 'Roboto Mono', monospace; font-size: 17px; color: var(--on); line-height: 1; }
.cc-stat-lbl { font-size: 10px; color: var(--on-v); margin-top: 2px; }

/* EQUIPMENT CARD */
.eq { background: var(--surf); border: 1px solid var(--out-v);
  border-radius: 12px; padding: 18px 22px;
  display: flex; flex-direction: column; gap: 14px; }
.eq-row { display: flex; align-items: center; gap: 14px; }
.eq-ico { width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 18px; }
.eq-lbl { font-size: 10px; font-weight: 500; letter-spacing: 0.5px;
  text-transform: uppercase; color: var(--on-v); }
.eq-val { font-family: 'Roboto Mono', monospace;
  font-size: 26px; font-weight: 400; color: var(--on); line-height: 1; }
.eq-foot { display: flex; align-items: center; gap: 8px; margin-top: 2px; }
.progtrack { height: 4px; border-radius: 2px; background: rgba(202,196,208,0.12); overflow: hidden; }
.progfill { height: 100%; border-radius: 2px; }
.gap-row { display: flex; gap: 8px; }
.gap-item { flex: 1; padding: 10px 14px; border-radius: 8px;
  background: var(--s-hi); border: 1px solid var(--out-v); }
.gap-who { font-size: 10px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
.gap-val { font-family: 'Roboto Mono', monospace; font-size: 17px; color: var(--on); line-height: 1.3; }
.gap-sub { font-size: 10px; color: var(--on-v); }

/* BIO METRIC TILE */
.mt { background: var(--surf); border-radius: 10px;
  border: 1px solid var(--out-v); border-top: 2px solid;
  padding: 10px 14px 8px; display: flex; flex-direction: column; gap: 5px; }
.mt-top { display: flex; align-items: center; justify-content: space-between; }
.mt-cat { font-size: 10px; font-weight: 500; letter-spacing: 0.5px;
  text-transform: uppercase; color: var(--on-v); }
.mt-ico { width: 24px; height: 24px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; }
.mt-num { font-family: 'Roboto Mono', monospace;
  font-size: 24px; font-weight: 400; color: var(--on);
  letter-spacing: -0.5px; line-height: 1; }
.mt-foot { display: flex; align-items: center; gap: 6px; }
.sb { font-size: 10px; font-weight: 500; letter-spacing: 0.5px; padding: 1px 6px; border-radius: 3px; }
.sb-ok   { background: rgba(77,182,172,0.14);  color: #4DB6AC; }
.sb-med  { background: rgba(255,183,77,0.14);   color: #FFB74D; }
.sb-bad  { background: rgba(239,154,154,0.14);  color: #EF9A9A; }
.sb-info { background: rgba(144,202,249,0.14);  color: #90CAF9; }
.mt-ctx { font-size: 10px; color: var(--on-v); opacity: 0.7; }

/* ACTIVITY TABLE */
.at { width: 100%; border-collapse: collapse; }
.at th { font-size: 10px; font-weight: 500; letter-spacing: 0.5px;
  text-transform: uppercase; color: var(--on-v);
  padding: 0 14px 10px; text-align: left; border-bottom: 1px solid var(--out-v); }
.at th:first-child { padding-left: 18px; }
.at td { font-size: 13px; color: var(--on); padding: 9px 14px;
  border-bottom: 1px solid var(--out-v); vertical-align: middle; }
.at td:first-child { padding-left: 18px; }
.at tr:last-child td { border-bottom: none; }
.al { display: inline-flex; align-items: center;
  font-size: 10px; font-weight: 500; letter-spacing: 0.5px; padding: 2px 7px; border-radius: 3px; }
.al-s { background: rgba(208,188,255,0.12); color: #D0BCFF; }
.al-r { background: rgba(128,203,196,0.12); color: #80CBC4; }
.al-o { background: rgba(202,196,208,0.10); color: #CAC4D0; }

/* SIM BADGE */
.sim { display: inline-flex; align-items: center;
  font-size: 10px; font-weight: 500; padding: 2px 6px; border-radius: 3px;
  background: rgba(255,224,130,0.12); color: #FFE082; margin-left: 8px; }

/* Streamlit overrides */
[data-testid="stExpander"] { background: var(--surf) !important;
  border: 1px solid var(--out-v) !important; border-radius: 12px !important; }
[data-testid="stExpander"] summary { color: var(--on-v) !important; }
.stButton > button[kind="primary"] {
  background: #D0BCFF !important; color: #381E72 !important;
  border: none !important; border-radius: 20px !important;
  font-weight: 500 !important; font-size: 14px !important; height: 40px !important; }
</style>
""", unsafe_allow_html=True)

# ── PATHS ──────────────────────────────────────────────────────────────────────
_here = Path(__file__).parent
_candidates = [_here.parent / "data", _here.parent / "hyrox-dashboard" / "data"]
DATA = next((p for p in _candidates if p.exists()), _candidates[0])
DB   = _here / "hyrox_review.db"

# ── SQLITE ─────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS weekly_review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        saved_at TEXT NOT NULL, week_label TEXT NOT NULL,
        item TEXT, my_feedback TEXT, partner_feedback TEXT)""")
    conn.commit(); conn.close()

def save_review(df, week_label):
    now = datetime.now().isoformat(timespec="seconds")
    rows = [(now, week_label, r["檢核項目"], r["Randall 的回饋"], r["Zoe 的回饋"])
            for _, r in df.iterrows()]
    conn = sqlite3.connect(DB)
    conn.executemany(
        "INSERT INTO weekly_review (saved_at,week_label,item,my_feedback,partner_feedback) VALUES(?,?,?,?,?)",
        rows)
    conn.commit(); conn.close()

def load_history():
    conn = sqlite3.connect(DB)
    df = pd.read_sql(
        "SELECT saved_at 儲存時間, week_label 週別, item 檢核項目,"
        " my_feedback Randall, partner_feedback Zoe"
        " FROM weekly_review ORDER BY saved_at DESC LIMIT 30", conn)
    conn.close(); return df

init_db()

# ── DATA LOADERS ───────────────────────────────────────────────────────────────
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
        sl  = sport.lower()
        tag = ("run" if any(w in sl for w in ["run","jog","cycling","swim","walk"])
               else "str" if any(w in sl for w in ["strength","weight"]) else "other")
        try: date_disp = datetime.strptime(date_str,"%Y-%m-%d").strftime("%m/%d")
        except: date_disp = date_str
        records.append({"date":date_disp,"name":loc or sport,"sport":sport,
                        "dur":dur,"hr":hr,"cal":cal,"tag":tag})
    return records[:5]

# ── SIMULATED TREND ────────────────────────────────────────────────────────────
random.seed(7)
today  = datetime.today()
dates_7 = [(today - timedelta(days=i)).strftime("%m/%d") for i in range(6,-1,-1)]
df_sim = pd.DataFrame({
    "日期":        dates_7,
    "Randall 負荷": [random.randint(42,88) for _ in range(7)],
    "Zoe 負荷":    [random.randint(38,82) for _ in range(7)],
    "Randall 配速": [round(random.uniform(5.8,7.2),2) for _ in range(7)],
    "Zoe 配速":    [round(random.uniform(6.2,7.8),2) for _ in range(7)],
})

r_total   = int(df_sim["Randall 負荷"].sum())
z_total   = int(df_sim["Zoe 負荷"].sum())
lead_diff = r_total - z_total
r_pace    = round(df_sim["Randall 配速"].mean(), 2)
z_pace    = round(df_sim["Zoe 配速"].mean(), 2)

def chart_base(reverse_y=False):
    base = dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto,system-ui", color="#CAC4D0", size=11),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color="rgba(202,196,208,0.55)", size=11),
                   linecolor="rgba(202,196,208,0.1)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(202,196,208,0.07)", zeroline=False,
                   tickfont=dict(color="rgba(202,196,208,0.55)", size=11)),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1,
                    font=dict(size=11, color="#CAC4D0"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=8, r=8, t=36, b=8),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#2B2930", bordercolor="rgba(202,196,208,0.2)",
                        font=dict(color="#E6E1E5", size=12)),
    )
    if reverse_y: base["yaxis"]["autorange"] = "reversed"
    return base

# ── LOAD ───────────────────────────────────────────────────────────────────────
h_raw  = load_json(DATA / "health.json")
a_raw  = load_json(DATA / "activities.json")
health = parse_health(h_raw)
acts   = parse_activities(a_raw)

race_date  = datetime(2027, 3, 13)
days_left  = (race_date - today).days
iso        = today.isocalendar()
week_label = f"{iso[0]}-W{iso[1]:02d}"

# ══════════════════════════════════════════════════════════════════════════════
# PAGE
# ══════════════════════════════════════════════════════════════════════════════

# ── 1  PAGE HEADER ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ph">
  <p class="ph-title">HYROX 雙人備賽戰情中心</p>
  <div class="ph-row">
    <span class="chip">Women's Doubles · 2027-03-13</span>
    <span class="chip chip-r">距離比賽 {days_left} 天</span>
    <span class="sync-lbl">已同步 {health['updated'] or '—'}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 2  WAR ROOM ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sh">
  <div class="sh-tag">WAR ROOM</div>
  <div class="sh-title">⚡ 本週戰況排名</div>
  <div class="sh-sub">每週日自動歸零 · Zoe 數據為 Strava 模擬（待串接）</div>
</div>
""", unsafe_allow_html=True)

if abs(lead_diff) < 3:
    lp_cls, lp_pts_cls = "lp-r", "lp-pts-r"
    lp_pts_str, lp_who = "TIE", "勢均力敵"
elif lead_diff > 0:
    lp_cls, lp_pts_cls = "lp-r", "lp-pts-r"
    lp_pts_str, lp_who = f"+{lead_diff}", "RANDALL 領先"
else:
    lp_cls, lp_pts_cls = "lp-z", "lp-pts-z"
    lp_pts_str, lp_who = f"+{abs(lead_diff)}", "ZOE 領先"

r_faster = r_pace < z_pace
r_pace_dl = "dl-r" if r_faster else "dl-n"
z_pace_dl = "dl-z" if not r_faster else "dl-n"
r_pace_tag = "✓ 較快" if r_faster else f"▲ +{round(r_pace-z_pace,2)}"
z_pace_tag = "✓ 較快" if not r_faster else f"▲ +{round(z_pace-r_pace,2)}"

st.markdown(f"""
<div class="wr">
  <div class="wr-standings">
    <div class="pc pc-r">
      <div class="pc-name pc-name-r">⚡ RANDALL · COROS</div>
      <div class="pc-score">{r_total}<span class="pc-unit"> pts</span></div>
      <div class="pc-sub">本週累積訓練負荷</div>
    </div>
    <div class="lp {lp_cls}">
      <div class="lp-pts {lp_pts_cls}">{lp_pts_str}</div>
      <div class="lp-lbl">{lp_who}</div>
    </div>
    <div class="pc pc-z">
      <div class="pc-name pc-name-z">★ ZOE · STRAVA</div>
      <div class="pc-score">{z_total}<span class="pc-unit"> pts</span></div>
      <div class="pc-sub">本週累積訓練負荷</div>
    </div>
  </div>
  <div class="wr-pace">
    <div class="wp">
      <div>
        <div class="wp-lbl">⚡ Randall · Zone 2 平均配速</div>
        <div class="wp-val">{r_pace} <span style="font-size:11px;color:#CAC4D0">min/km</span></div>
      </div>
      <span class="dl {r_pace_dl}">{r_pace_tag}</span>
    </div>
    <div class="wp">
      <div>
        <div class="wp-lbl">★ Zoe · Zone 2 平均配速</div>
        <div class="wp-val">{z_pace} <span style="font-size:11px;color:#CAC4D0">min/km</span></div>
      </div>
      <span class="dl {z_pace_dl}">{z_pace_tag}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 3  BATTLEGROUND ────────────────────────────────────────────────────────────
st.markdown("""
<div class="sh">
  <div class="sh-tag">BATTLEGROUND</div>
  <div class="sh-title">📊 七日訓練對比</div>
</div>
""", unsafe_allow_html=True)

cl, cr = st.columns(2)

with cl:
    st.markdown('<div class="cc"><div class="cc-title">訓練負荷</div><div class="cc-sub">Training Load · RANDALL vs ZOE <span class="sim">⚠ 模擬</span></div>', unsafe_allow_html=True)
    fig = go.Figure()
    for name, col, color, fill in [
        ("⚡ Randall", "Randall 負荷", "#D0BCFF", "rgba(208,188,255,0.10)"),
        ("★ Zoe",     "Zoe 負荷",    "#60A5FA", "rgba(96,165,250,0.08)"),
    ]:
        fig.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=name, mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.6),
            marker=dict(size=6, color=color, line=dict(width=1.5, color="#211F26")),
            fill="tozeroy", fillcolor=fill,
            hovertemplate="%{y} pts",
        ))
    fig.update_layout(**chart_base(), height=220)
    st.plotly_chart(fig, use_container_width=True)
    lead_dl = "dl-r" if lead_diff >= 0 else "dl-z"
    lead_sign = "+" if lead_diff >= 0 else ""
    st.markdown(f"""
    <div class="cc-stats">
      <div class="cc-stat">
        <div class="cc-stat-val" style="color:#D0BCFF">{r_total}</div>
        <div class="cc-stat-lbl">⚡ Randall 本週</div>
      </div>
      <div class="cc-stat">
        <div class="cc-stat-val" style="color:#60A5FA">{z_total}</div>
        <div class="cc-stat-lbl">★ Zoe 本週</div>
      </div>
      <div class="cc-stat">
        <div class="cc-stat-val"><span class="dl {lead_dl}">{lead_sign}{lead_diff}</span></div>
        <div class="cc-stat-lbl">差距 (pts)</div>
      </div>
    </div>""", unsafe_allow_html=True)

with cr:
    pace_diff = round(r_pace - z_pace, 2)
    pace_dl = "dl-r" if pace_diff <= 0 else "dl-z"
    pace_sign = "+" if pace_diff >= 0 else ""
    st.markdown('<div class="cc"><div class="cc-title">Zone 2 配速</div><div class="cc-sub">min/km · 數值越小代表越快 <span class="sim">⚠ 模擬</span></div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for name, col, color, fill in [
        ("⚡ Randall", "Randall 配速", "#D0BCFF", "rgba(208,188,255,0.10)"),
        ("★ Zoe",     "Zoe 配速",    "#60A5FA", "rgba(96,165,250,0.08)"),
    ]:
        fig2.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=name, mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.6),
            marker=dict(size=6, color=color, line=dict(width=1.5, color="#211F26")),
            fill="tozeroy", fillcolor=fill,
            hovertemplate="%{y} min/km",
        ))
    fig2.update_layout(**chart_base(reverse_y=True), height=220)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(f"""
    <div class="cc-stats">
      <div class="cc-stat">
        <div class="cc-stat-val" style="color:#D0BCFF">{r_pace}</div>
        <div class="cc-stat-lbl">⚡ Randall 平均</div>
      </div>
      <div class="cc-stat">
        <div class="cc-stat-val" style="color:#60A5FA">{z_pace}</div>
        <div class="cc-stat-lbl">★ Zoe 平均</div>
      </div>
      <div class="cc-stat">
        <div class="cc-stat-val"><span class="dl {pace_dl}">{pace_sign}{pace_diff}</span></div>
        <div class="cc-stat-lbl">差距 (min/km)</div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── 4  TEAM READINESS ──────────────────────────────────────────────────────────
st.markdown("""
<div class="sh">
  <div class="sh-tag">TEAM READINESS</div>
  <div class="sh-title">🎯 器材備戰</div>
  <div class="sh-sub">Women's Doubles 官方標準</div>
</div>
""", unsafe_allow_html=True)

eq1, eq2 = st.columns(2)

with eq1:
    st.markdown("""
    <div class="eq">
      <div class="eq-row">
        <div class="eq-ico" style="background:rgba(77,182,172,0.12)">🏋️</div>
        <div>
          <div class="eq-lbl">Sled Push</div>
          <div class="eq-val">102 kg</div>
          <div class="eq-foot">
            <span class="sb sb-ok">✓ 達標</span>
            <span style="font-size:11px;color:#CAC4D0">標準 102 kg</span>
          </div>
        </div>
      </div>
      <div class="progtrack">
        <div class="progfill" style="width:100%;background:#4DB6AC"></div>
      </div>
      <div class="gap-row">
        <div class="gap-item">
          <div class="gap-who" style="color:#D0BCFF">⚡ Randall</div>
          <div class="gap-val">102 kg</div>
          <div class="gap-sub">上次測試</div>
        </div>
        <div class="gap-item">
          <div class="gap-who" style="color:#60A5FA">★ Zoe</div>
          <div class="gap-val">105 kg</div>
          <div class="gap-sub">上次測試 ↑ +3</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

with eq2:
    wb_cur, wb_tgt = 58, 75
    wb_pct = round(wb_cur / wb_tgt * 100)
    wb_gap = wb_tgt - wb_cur
    st.markdown(f"""
    <div class="eq">
      <div class="eq-row">
        <div class="eq-ico" style="background:rgba(239,154,154,0.12)">🎯</div>
        <div>
          <div class="eq-lbl">Wall Balls · 4 kg</div>
          <div class="eq-val">{wb_cur} <span style="font-size:16px;color:#CAC4D0">/ {wb_tgt}</span></div>
          <div class="eq-foot">
            <span class="sb sb-bad">差 {wb_gap} 下</span>
            <span style="font-size:11px;color:#CAC4D0">{wb_pct}% 達標</span>
          </div>
        </div>
      </div>
      <div class="progtrack">
        <div class="progfill" style="width:{wb_pct}%;background:#EF9A9A"></div>
      </div>
      <div class="gap-row">
        <div class="gap-item">
          <div class="gap-who" style="color:#D0BCFF">⚡ Randall</div>
          <div class="gap-val">{wb_cur} 下</div>
          <div class="gap-sub">最新測試</div>
        </div>
        <div class="gap-item">
          <div class="gap-who" style="color:#60A5FA">★ Zoe</div>
          <div class="gap-val">— 下</div>
          <div class="gap-sub">待測試</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── 5  MISSION DEBRIEF ─────────────────────────────────────────────────────────
st.markdown("""
<div class="sh">
  <div class="sh-tag">MISSION DEBRIEF</div>
  <div class="sh-title">📋 每週戰略盤點</div>
  <div class="sh-sub">填寫後儲存到本地 SQLite · 每週日同步</div>
</div>
""", unsafe_allow_html=True)

default_df = pd.DataFrame({
    "檢核項目":     ["本週主觀疲勞 (RPE 1-10)", "Sled Push 重量達標情形", "下週合練重點"],
    "Randall 的回饋": ["", "", ""],
    "Zoe 的回饋":     ["", "", ""],
})
edited_df = st.data_editor(
    default_df, use_container_width=True, hide_index=True, num_rows="fixed",
    column_config={
        "檢核項目":      st.column_config.TextColumn("檢核項目", disabled=True, width="medium"),
        "Randall 的回饋": st.column_config.TextColumn("⚡ Randall 的回饋", width="large"),
        "Zoe 的回饋":     st.column_config.TextColumn("★ Zoe 的回饋",     width="large"),
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

# ── 6  BIO-READINESS ───────────────────────────────────────────────────────────
st.markdown("""
<div class="sh">
  <div class="sh-tag">BIO-READINESS</div>
  <div class="sh-title">🩺 個人生物備戰</div>
  <div class="sh-sub">COROS 自動同步 · Randall 個人數據</div>
</div>
""", unsafe_allow_html=True)

def classify(key, val):
    try: n = int(str(val).replace("%",""))
    except: return "sb-info", "—"
    if key == "recovery":
        if n >= 75: return "sb-ok", "優良"
        if n >= 50: return "sb-med", "普通"
        return "sb-bad", "偏低"
    if key == "sleep":
        if n >= 70: return "sb-ok", "良好"
        if n >= 50: return "sb-med", "普通"
        return "sb-bad", "不足"
    if key == "hr":
        if n <= 55: return "sb-ok", "低強度"
        if n <= 65: return "sb-med", "正常"
        return "sb-bad", "偏高"
    if key == "stress":
        if n <= 25: return "sb-ok", "放鬆"
        if n <= 50: return "sb-med", "輕度"
        return "sb-bad", "高壓"
    return "sb-info", "—"

r_cls, r_lbl   = classify("recovery", health["recovery"])
s_cls, s_lbl   = classify("sleep",    health["sleep_score"])
h_cls, h_lbl   = classify("hr",       health["hr"])
st_cls, st_lbl = classify("stress",   health["stress"])
if health["stress_label"]: st_lbl = health["stress_label"]

ICON_SVG = {
    "recovery": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "sleep":    '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    "hr":       '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "stress":   '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
}

TILES = [
    ("recovery","恢復狀態","#D0BCFF","rgba(208,188,255,0.10)",
     health["recovery"], r_cls, r_lbl, health["recovery_level"] or "COROS"),
    ("sleep","睡眠評分","#80CBC4","rgba(128,203,196,0.10)",
     health["sleep_score"], s_cls, s_lbl, health["sleep_dur"] or "今晚"),
    ("hr","靜止心率","#90CAF9","rgba(144,202,249,0.10)",
     health["hr"]+" bpm" if health["hr"]!="—" else "—", h_cls, h_lbl, "今日"),
    ("stress","壓力指數","#FFE082","rgba(255,224,130,0.10)",
     health["stress"], st_cls, st_lbl, health["stress_label"] or "—"),
]

bio_cols = st.columns(4)
for (key, label, color, iconbg, val, cls, badge, ctx), col in zip(TILES, bio_cols):
    with col:
        st.markdown(f"""
        <div class="mt" style="border-top-color:{color}">
          <div class="mt-top">
            <span class="mt-cat">{label}</span>
            <div class="mt-ico" style="background:{iconbg};color:{color}">{ICON_SVG[key]}</div>
          </div>
          <div class="mt-num">{val}</div>
          <div class="mt-foot">
            <span class="sb {cls}">{badge}</span>
            <span class="mt-ctx">{ctx}</span>
          </div>
        </div>""", unsafe_allow_html=True)

# ── 7  TRAINING LOG ────────────────────────────────────────────────────────────
with st.expander("📋 Show Full Training Log — Randall · COROS", expanded=False):
    if acts:
        label_map = {"str":"肌力","run":"有氧","other":"其他"}
        label_cls  = {"str":"al-s","run":"al-r","other":"al-o"}
        rows_html = ""
        for a in acts:
            sport_short = (a["sport"].replace("Custom Indoor Other","室內")
                                     .replace("Strength","肌力訓練"))
            lbl  = label_map.get(a["tag"],"—")
            lcls = label_cls.get(a["tag"],"al-o")
            rows_html += f"""<tr>
              <td style="color:#CAC4D0;font-size:12px">{a['date']}</td>
              <td><span style="color:#E6E1E5;font-weight:500">{a['name']}</span>
                  <span style="color:#CAC4D0;font-size:12px;margin-left:6px">· {sport_short}</span></td>
              <td><span class="al {lcls}">{lbl}</span></td>
              <td>{a['dur']}</td><td>{a['hr']}</td>
              <td style="color:#CAC4D0">{a['cal']}</td></tr>"""
        st.markdown(f"""
        <table class="at">
          <thead><tr>
            <th>日期</th><th>項目</th><th>類型</th>
            <th>時長</th><th>平均心率</th><th>消耗</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)
    else:
        st.caption("尚無運動記錄 — 等待 GitHub Actions 同步 COROS 資料")
