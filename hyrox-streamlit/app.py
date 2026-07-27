import re, sqlite3, json, base64
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import random
import urllib.request

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
  --bg:      #0D1117;
  --surf:    #161B22;
  --s-hi:    #1C2128;
  --s-top:   #21262D;
  --on:      #E6EDF3;
  --on-v:    #8B949E;
  --out:     rgba(48,54,61,0.8);
  --out-v:   rgba(48,54,61,0.4);
  --r:       #58A6FF;
  --r-bg:    rgba(88,166,255,0.10);
  --r-bd:    rgba(88,166,255,0.22);
  --z:       #E3B341;
  --z-bg:    rgba(227,179,65,0.10);
  --z-bd:    rgba(227,179,65,0.22);
  --ok:      #E3B341;
  --wrn:     #E3B341;
  --err:     #F85149;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'Roboto', system-ui, sans-serif;
  color: var(--on); font-size: 16px; line-height: 1.5;
}
.block-container { padding: 20px 16px 72px !important; max-width: 100% !important; }

/* PAGE HEADER */
.ph { padding-bottom: 14px; border-bottom: 1px solid var(--out); margin-bottom: 0; }
.ph-title { font-size: 20px; font-weight: 400; margin: 0 0 6px; }
.ph-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.chip { display: inline-flex; align-items: center; height: 26px; padding: 0 10px;
  border: 1px solid var(--out); border-radius: 6px;
  font-size: 12px; font-weight: 500; color: var(--on-v); }
.chip-r { background: var(--r-bg); border-color: var(--r-bd); color: var(--r); }
.sync-lbl { font-size: 11px; color: rgba(139,148,158,0.5); margin-left: auto; }

/* SECTION HEADER */
.sh { margin: 28px 0 14px; }
.sh-tag { font-size: 11px; font-weight: 500; letter-spacing: 1.5px;
  text-transform: uppercase; color: var(--on-v); margin-bottom: 3px; }
.sh-title { font-size: 20px; font-weight: 400; color: var(--on); margin: 0; }
.sh-sub { font-size: 12px; color: var(--on-v); margin-top: 2px; }

/* WAR ROOM */
.wr { background: var(--surf); border: 1px solid var(--out);
  border-radius: 16px; padding: 22px 24px 18px; }
/* Score header */
.wr-scores { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 20px; }
.ws-player { flex: 1; }
.ws-player-z { text-align: right; }
.ws-name { font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }
.ws-name-r { color: var(--r); }
.ws-name-z { color: var(--z); }
.ws-score { font-family: 'Roboto Mono', monospace;
  font-size: 44px; font-weight: 400; line-height: 1; letter-spacing: -1.5px; color: var(--on); }
.ws-unit { font-size: 15px; color: var(--on-v); font-weight: 400; }
.ws-pct { font-size: 12px; font-weight: 500; margin-top: 5px; }
.ws-mid { text-align: center; padding-bottom: 6px; flex-shrink: 0; }
.ws-lead-pts { font-family: 'Roboto Mono', monospace; font-size: 26px; font-weight: 400; line-height: 1; }
.ws-lead-lbl { font-size: 11px; font-weight: 500; letter-spacing: 0.5px; color: var(--on-v); margin-top: 3px; }
/* Battle (tug-of-war) bar */
.bb-wrap { margin: 0 0 18px; }
.bb-track { height: 18px; border-radius: 9px; overflow: hidden; position: relative; }
.bb-r { position: absolute; left: 0; top: 0; bottom: 0;
  background: linear-gradient(90deg, rgba(88,166,255,0.5) 0%, #58A6FF 100%);
  border-radius: 9px 0 0 9px; }
.bb-z { position: absolute; right: 0; top: 0; bottom: 0;
  background: linear-gradient(270deg, rgba(227,179,65,0.5) 0%, #E3B341 100%);
  border-radius: 0 9px 9px 0; }
.bb-mid-line { position: absolute; top: 0; bottom: 0; width: 2px;
  background: rgba(13,17,23,0.85); left: calc(50% - 1px); }
.bb-labels { display: flex; justify-content: space-between; align-items: center;
  margin-top: 7px; font-size: 12px; }
/* Pace visual bars */
.pv { background: var(--s-hi); border: 1px solid var(--out-v);
  border-radius: 10px; padding: 14px 18px; }
.pv-title { font-size: 11px; font-weight: 500; letter-spacing: 0.8px;
  text-transform: uppercase; color: var(--on-v); margin-bottom: 12px; }
.pv-row { display: flex; align-items: center; gap: 10px; }
.pv-row + .pv-row { margin-top: 10px; }
.pv-name { font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
  text-transform: uppercase; width: 76px; flex-shrink: 0; }
.pv-track { flex: 1; height: 8px; border-radius: 4px;
  background: rgba(48,54,61,0.4); overflow: hidden; }
.pv-fill { height: 100%; border-radius: 4px; }
.pv-val { font-family: 'Roboto Mono', monospace; font-size: 13px; width: 58px;
  text-align: right; flex-shrink: 0; }
.dl { font-size: 12px; padding: 2px 7px; border-radius: 4px; font-weight: 500; }
.dl-r { background: var(--r-bg); color: var(--r); }
.dl-z { background: var(--z-bg); color: var(--z); }
.dl-n { background: rgba(48,54,61,0.4); color: var(--on-v); }

/* CHART CARD */
.cc { background: var(--surf); border: 1px solid var(--out-v);
  border-radius: 12px; padding: 16px 16px 6px; }
.cc-title { font-size: 14px; font-weight: 500; color: var(--on); margin-bottom: 2px; }
.cc-sub { font-size: 12px; color: var(--on-v); margin-bottom: 8px; }
.cc-stats { display: flex; padding-top: 6px; border-top: 1px solid var(--out-v); }
.cc-stat { flex: 1; padding: 8px 12px; border-right: 1px solid var(--out-v); }
.cc-stat:last-child { border-right: none; }
.cc-stat-val { font-family: 'Roboto Mono', monospace; font-size: 17px; color: var(--on); line-height: 1; }
.cc-stat-lbl { font-size: 11px; color: var(--on-v); margin-top: 2px; }

/* EQUIPMENT CARD */
.eq { background: var(--surf); border: 1px solid var(--out-v);
  border-radius: 12px; padding: 18px 22px;
  display: flex; flex-direction: column; gap: 14px; }
.eq-row { display: flex; align-items: center; gap: 14px; }
.eq-ico { width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 18px; }
.eq-lbl { font-size: 11px; font-weight: 500; letter-spacing: 0.5px;
  text-transform: uppercase; color: var(--on-v); }
.eq-val { font-family: 'Roboto Mono', monospace;
  font-size: 26px; font-weight: 400; color: var(--on); line-height: 1; }
.eq-foot { display: flex; align-items: center; gap: 8px; margin-top: 2px; }
.progtrack { height: 4px; border-radius: 2px; background: rgba(48,54,61,0.6); overflow: hidden; }
.progfill { height: 100%; border-radius: 2px; }
.gap-row { display: flex; gap: 8px; }
.gap-item { flex: 1; padding: 10px 14px; border-radius: 8px;
  background: var(--s-hi); border: 1px solid var(--out-v); }
.gap-who { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
.gap-val { font-family: 'Roboto Mono', monospace; font-size: 17px; color: var(--on); line-height: 1.3; }
.gap-sub { font-size: 11px; color: var(--on-v); }

/* BIO METRIC TILE */
.mt { background: var(--surf); border-radius: 10px;
  border: 1px solid var(--out-v); border-top: 2px solid;
  padding: 10px 14px 8px; display: flex; flex-direction: column; gap: 5px; }
.mt-top { display: flex; align-items: center; justify-content: space-between; }
.mt-cat { font-size: 11px; font-weight: 500; letter-spacing: 0.5px;
  text-transform: uppercase; color: var(--on-v); }
.mt-ico { width: 24px; height: 24px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; }
.mt-num { font-family: 'Roboto Mono', monospace;
  font-size: 24px; font-weight: 400; color: var(--on);
  letter-spacing: -0.5px; line-height: 1; }
.mt-foot { display: flex; align-items: center; gap: 6px; }
.sb { font-size: 11px; font-weight: 500; letter-spacing: 0.5px; padding: 2px 7px; border-radius: 3px; }
.sb-ok   { background: rgba(227,179,65,0.14);  color: #E3B341; }
.sb-med  { background: rgba(227,179,65,0.14);   color: #E3B341; }
.sb-bad  { background: rgba(248,81,73,0.14);  color: #F85149; }
.sb-info { background: rgba(121,192,255,0.14);  color: #79C0FF; }
.mt-ctx { font-size: 11px; color: var(--on-v); opacity: 0.7; }

/* ACTIVITY TABLE */
.at { width: 100%; border-collapse: collapse; }
.at th { font-size: 11px; font-weight: 500; letter-spacing: 0.5px;
  text-transform: uppercase; color: var(--on-v);
  padding: 0 14px 10px; text-align: left; border-bottom: 1px solid var(--out-v); }
.at th:first-child { padding-left: 18px; }
.at td { font-size: 13px; color: var(--on); padding: 9px 14px;
  border-bottom: 1px solid var(--out-v); vertical-align: middle; }
.at td:first-child { padding-left: 18px; }
.at tr:last-child td { border-bottom: none; }
.al { display: inline-flex; align-items: center;
  font-size: 11px; font-weight: 500; letter-spacing: 0.5px; padding: 2px 7px; border-radius: 3px; }
.al-s { background: rgba(88,166,255,0.12); color: #58A6FF; }
.al-r { background: rgba(227,179,65,0.12); color: #E3B341; }
.al-o { background: rgba(48,54,61,0.5); color: #8B949E; }

/* SIM BADGE */
.sim { display: inline-flex; align-items: center;
  font-size: 11px; font-weight: 500; padding: 2px 6px; border-radius: 3px;
  background: rgba(227,179,65,0.12); color: #E3B341; margin-left: 8px; }

/* STRAVA CONNECT */
.sc { background: var(--surf); border: 1px solid var(--out-v);
  border-radius: 14px; padding: 22px 24px; }
.sc-row { display: flex; align-items: center; gap: 16px; }
.sc-avatar { width: 44px; height: 44px; border-radius: 22px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; flex-shrink: 0; }
.sc-name { font-size: 13px; font-weight: 500; color: var(--on); }
.sc-meta { font-size: 11px; color: var(--on-v); margin-top: 2px; }
.sc-stat-row { display: flex; gap: 0; margin-top: 16px; border: 1px solid var(--out-v);
  border-radius: 10px; overflow: hidden; }
.sc-stat { flex: 1; padding: 10px 14px; border-right: 1px solid var(--out-v); }
.sc-stat:last-child { border-right: none; }
.sc-stat-val { font-family: 'Roboto Mono', monospace; font-size: 16px; color: var(--on); }
.sc-stat-lbl { font-size: 11px; color: var(--on-v); margin-top: 1px; }

/* Streamlit overrides */
[data-testid="stExpander"] { background: var(--surf) !important;
  border: 1px solid var(--out-v) !important; border-radius: 12px !important; }
[data-testid="stExpander"] summary { color: var(--on-v) !important; }
.stButton > button[kind="primary"] {
  background: #58A6FF !important; color: #0D1117 !important;
  border: none !important; border-radius: 20px !important;
  font-weight: 500 !important; font-size: 14px !important; height: 40px !important; }

/* ── MOBILE FIRST ──────────────────────────────────────────── */
@media (max-width: 640px) {
  /* Stack all st.columns() vertically */
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 8px !important; }
  [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }

  /* Page header */
  .ph-title  { font-size: 18px; }
  .chip      { font-size: 13px; height: 30px; padding: 0 12px; }
  .sync-lbl  { font-size: 12px; }

  /* Section header */
  .sh       { margin: 22px 0 12px; }
  .sh-tag   { font-size: 12px; }
  .sh-title { font-size: 20px; }
  .sh-sub   { font-size: 13px; }

  /* Card padding */
  .wr { padding: 16px 16px 14px; border-radius: 14px; }
  .sc { padding: 16px 16px; border-radius: 12px; }
  .cc { padding: 14px 14px 6px; }
  .eq { padding: 14px 16px; gap: 12px; }
  .mt { padding: 12px 12px 10px; }

  /* Score card - player names */
  .ws-name    { font-size: 12px; letter-spacing: 0.8px; }
  .ws-score   { font-size: 36px !important; letter-spacing: -1px; }
  .ws-unit    { font-size: 14px; }
  .ws-pct     { font-size: 13px; }
  .ws-lead-pts { font-size: 22px !important; }
  .ws-lead-lbl { font-size: 12px; }

  /* Battle bar labels */
  .bb-labels  { font-size: 13px; margin-top: 8px; }
  .bb-track   { height: 20px; border-radius: 10px; }

  /* Pace section */
  .pv         { padding: 14px 16px; }
  .pv-title   { font-size: 12px; margin-bottom: 14px; }
  .pv-row     { gap: 10px; }
  .pv-row + .pv-row { margin-top: 12px; }
  .pv-name    { font-size: 12px; width: 72px; }
  .pv-track   { height: 10px; border-radius: 5px; }
  .pv-val     { font-size: 15px; width: 52px; }
  .dl         { font-size: 12px; padding: 3px 8px; }

  /* Chart card */
  .cc-title   { font-size: 15px; }
  .cc-sub     { font-size: 13px; margin-bottom: 10px; }
  .cc-stat-val { font-size: 16px; }
  .cc-stat-lbl { font-size: 12px; }

  /* Equipment card */
  .eq-lbl { font-size: 12px; }
  .eq-val { font-size: 24px; }
  .gap-who { font-size: 12px; }
  .gap-val { font-size: 16px; }
  .gap-sub { font-size: 12px; }

  /* Bio metric tile */
  .mt-cat { font-size: 12px; }
  .mt-num { font-size: 22px; }
  .sb     { font-size: 11px; padding: 2px 7px; }
  .mt-ctx { font-size: 11px; }

  /* Activity table */
  .at th  { font-size: 12px; padding: 0 10px 10px; }
  .at td  { font-size: 14px; padding: 10px 10px; }
  .al     { font-size: 11px; padding: 3px 8px; }

  /* Stats card (athlete summary) */
  .sc-name    { font-size: 14px; }
  .sc-meta    { font-size: 12px; }
  .sc-stat-row { flex-wrap: wrap; }
  .sc-stat    { min-width: 50%; padding: 12px 14px; }
  .sc-stat-val { font-size: 16px; }
  .sc-stat-lbl { font-size: 12px; margin-top: 2px; }

  /* Touch-friendly form inputs (prevent iOS zoom) */
  [data-testid="stNumberInput"] input,
  [data-testid="stTextInput"] input,
  [data-testid="stSelectbox"] select,
  [data-testid="stDateInput"] input { min-height: 44px !important; font-size: 16px !important; }

  /* Expander touch target */
  [data-testid="stExpander"] summary { min-height: 48px !important; display: flex !important;
    align-items: center !important; font-size: 14px !important; }

  /* Chart overflow guard */
  [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"],
  [data-testid="stPlotlyChart"] { max-width: 100% !important; overflow-x: hidden !important; }

  /* Submit button - full width, taller */
  .stButton > button[kind="primary"] { height: 48px !important; font-size: 16px !important;
    width: 100% !important; border-radius: 14px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── PATHS ──────────────────────────────────────────────────────────────────────
_here = Path(__file__).parent
_candidates = [_here.parent / "data", _here.parent / "hyrox-dashboard" / "data"]
DATA = next((p for p in _candidates if p.exists()), _candidates[0])
DB   = _here / "hyrox_review.db"

# ── GITHUB WRITE-BACK ──────────────────────────────────────────────────────────
_GH_REPO      = "Randall2000/coros"
_GH_FILE_PATH = "data/strava.json"
_GH_API_BASE  = "https://api.github.com"

def _gh_get(token: str, path: str) -> dict:
    req = urllib.request.Request(
        f"{_GH_API_BASE}{path}",
        headers={"Authorization": f"token {token}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "hyrox-app"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def _gh_put(token: str, path: str, payload: dict):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{_GH_API_BASE}{path}", data=data, method="PUT",
        headers={"Authorization": f"token {token}",
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json",
                 "User-Agent": "hyrox-app"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def _pace_to_float(pace_str: str) -> float | None:
    """'5:30' → 5.5"""
    try:
        m, s = pace_str.strip().split(":")
        return round(int(m) + int(s) / 60, 4)
    except Exception:
        return None

def write_zoe_activity(new_act: dict) -> tuple[bool, str]:
    """新增一筆 Zoe 訓練，寫回 GitHub strava.json。回傳 (ok, message)。"""
    token = st.secrets.get("GITHUB_TOKEN", "")
    if not token:
        return False, "未設定 GITHUB_TOKEN secret，無法儲存"
    try:
        info = _gh_get(token, f"/repos/{_GH_REPO}/contents/{_GH_FILE_PATH}")
        sha  = info["sha"]
        old  = json.loads(base64.b64decode(info["content"]).decode())
    except Exception:
        sha  = None
        old  = {"source": "manual", "updatedAt": "", "activities_7d": [], "summary_7d": {}}

    old.setdefault("activities_7d", [])
    old["activities_7d"].insert(0, new_act)
    cutoff = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    old["activities_7d"] = [a for a in old["activities_7d"] if a.get("date", "") >= cutoff]

    acts7 = old["activities_7d"]
    total_load = sum(a.get("training_load", 0) for a in acts7)
    total_km   = round(sum(a.get("distance_km", 0) for a in acts7), 2)
    paces      = [a["avg_pace_float"] for a in acts7 if a.get("avg_pace_float")]
    avg_pace_f = round(sum(paces) / len(paces), 4) if paces else None
    avg_pace_s = f"{int(avg_pace_f)}:{round((avg_pace_f % 1)*60):02d}" if avg_pace_f else "—"

    old["source"]     = "manual"
    old["updatedAt"]  = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    old["summary_7d"] = {
        "total_load":        total_load,
        "total_distance_km": total_km,
        "avg_pace":          avg_pace_s,
        "avg_pace_float":    avg_pace_f,
        "activity_count":    len(acts7),
    }
    content_b64 = base64.b64encode(json.dumps(old, ensure_ascii=False, indent=2).encode()).decode()
    payload = {"message": f"data: Zoe 手動新增 {new_act['date']} {new_act['name']}",
               "content": content_b64}
    if sha:
        payload["sha"] = sha
    _gh_put(token, f"/repos/{_GH_REPO}/contents/{_GH_FILE_PATH}", payload)
    return True, "已儲存！"

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

def parse_intervals(s: dict) -> dict:
    """Parse data/strava.json (written by fetch_intervals.py)."""
    empty = {"source": None, "updated": "", "activities": [],
             "total_load": 0, "avg_pace": "—", "avg_pace_float": None,
             "total_km": 0, "atl": None, "ctl": None, "count": 0,
             "by_day": {}}
    if not s or s.get("source") not in ("intervals.icu", "strava", "manual"):
        return empty
    summ = s.get("summary_7d", {})
    acts = s.get("activities_7d", [])
    by_day: dict[str, int] = {}
    by_day_pace: dict[str, list] = {}
    for a in acts:
        d = a.get("date", "")
        by_day[d]      = by_day.get(d, 0) + (a.get("training_load") or 0)
        if a.get("avg_pace_float"):
            by_day_pace.setdefault(d, []).append(a["avg_pace_float"])
    ts = s.get("updatedAt", "")
    try:
        updated = datetime.fromisoformat(ts.replace("Z","+00:00")).strftime("%m/%d %H:%M")
    except Exception:
        updated = ts[:16]
    return {
        "source":         s.get("source"),
        "updated":        updated,
        "activities":     acts,
        "total_load":     summ.get("total_load", 0),
        "avg_pace":       summ.get("avg_pace", "—"),
        "avg_pace_float": summ.get("avg_pace_float"),
        "total_km":       summ.get("total_distance_km", 0),
        "atl":            summ.get("atl"),
        "ctl":            summ.get("ctl"),
        "count":          summ.get("activity_count", 0),
        "by_day":         by_day,
        "by_day_pace":    by_day_pace,
    }

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

# ── LOAD ───────────────────────────────────────────────────────────────────────
h_raw  = load_json(DATA / "health.json")
a_raw  = load_json(DATA / "activities.json")
s_raw  = load_json(DATA / "strava.json")
health = parse_health(h_raw)
acts   = parse_activities(a_raw)
zoe    = parse_intervals(s_raw)

# ── TREND DATA ─────────────────────────────────────────────────────────────────
random.seed(7)
today     = datetime.today()
dates_iso = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6,-1,-1)]
dates_7   = [(today - timedelta(days=i)).strftime("%m/%d")    for i in range(6,-1,-1)]

_zoe_has_real  = bool(zoe["source"])
_zoe_is_manual = zoe.get("source") == "manual"
_zoe_source_lbl = ("手動輸入" if _zoe_is_manual
                   else "intervals.icu" if _zoe_has_real
                   else "模擬")

# Zoe load: use real by-day sums when available, fall back to simulation
_rand_zoe_load  = [random.randint(38, 82) for _ in range(7)]
_rand_zoe_pace  = [round(random.uniform(6.2, 7.8), 2) for _ in range(7)]
_rand_r_load    = [random.randint(42, 88) for _ in range(7)]
_rand_r_pace    = [round(random.uniform(5.8, 7.2), 2) for _ in range(7)]

_zoe_loads = [zoe["by_day"].get(d, _rand_zoe_load[i]) for i, d in enumerate(dates_iso)]
_zoe_paces = []
for i, d in enumerate(dates_iso):
    real_paces = zoe.get("by_day_pace", {}).get(d)
    _zoe_paces.append(round(sum(real_paces)/len(real_paces), 2) if real_paces else _rand_zoe_pace[i])

df_sim = pd.DataFrame({
    "日期":         dates_7,
    "Randall 負荷": _rand_r_load,
    "Zoe 負荷":     _zoe_loads,
    "Randall 配速": _rand_r_pace,
    "Zoe 配速":     _zoe_paces,
})

r_total   = int(df_sim["Randall 負荷"].sum())
z_total   = int(df_sim["Zoe 負荷"].sum())
lead_diff = r_total - z_total
r_pace    = round(df_sim["Randall 配速"].mean(), 2)
z_pace    = round(df_sim["Zoe 配速"].mean(), 2)
r_cum     = df_sim["Randall 負荷"].cumsum().tolist()
z_cum     = df_sim["Zoe 負荷"].cumsum().tolist()

def chart_base(reverse_y=False):
    base = dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Roboto,system-ui", color="#8B949E", size=11),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color="rgba(139,148,158,0.7)", size=11),
                   linecolor="rgba(48,54,61,0.6)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(48,54,61,0.35)", zeroline=False,
                   tickfont=dict(color="rgba(139,148,158,0.7)", size=11)),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1,
                    font=dict(size=11, color="#8B949E"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=8, r=8, t=36, b=8),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1C2128", bordercolor="rgba(48,54,61,0.8)",
                        font=dict(color="#E6EDF3", size=12)),
    )
    if reverse_y: base["yaxis"]["autorange"] = "reversed"
    return base

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
  <div class="sh-sub">每週日自動歸零 · Zoe 每日手動輸入</div>
</div>
""", unsafe_allow_html=True)

# Battle bar calculations
_total  = r_total + z_total
r_pct   = round(r_total / _total * 100)
z_pct   = 100 - r_pct

if abs(lead_diff) < 3:
    lp_color, lp_pts_str, lp_who = "#8B949E", "TIE", "勢均力敵"
elif lead_diff > 0:
    lp_color, lp_pts_str, lp_who = "#58A6FF", f"+{lead_diff}", "RANDALL 領先"
else:
    lp_color, lp_pts_str, lp_who = "#E3B341", f"+{abs(lead_diff)}", "ZOE 領先"

# Pace visual bar (lower = faster; scale to 8.0 min/km max)
_pace_scale = 8.0
r_bar = round(r_pace / _pace_scale * 100)
z_bar = round(z_pace / _pace_scale * 100)
r_faster = r_pace < z_pace
r_pace_dl = "dl-r" if r_faster else "dl-n"
z_pace_dl = "dl-z" if not r_faster else "dl-n"
r_pace_tag = "✓ 較快" if r_faster else f"▲ +{round(r_pace-z_pace,2)}"
z_pace_tag = "✓ 較快" if not r_faster else f"▲ +{round(z_pace-r_pace,2)}"

# Battle bar background = Zoe's colour (blue), Randall fills from left (purple)
st.markdown(f"""
<div class="wr">
  <!-- Score header -->
  <div class="wr-scores">
    <div class="ws-player">
      <div class="ws-name ws-name-r">⚡ RANDALL · COROS</div>
      <div class="ws-score">{r_total}<span class="ws-unit"> pts</span></div>
      <div class="ws-pct" style="color:#58A6FF">{r_pct}% 本週份額</div>
    </div>
    <div class="ws-mid">
      <div class="ws-lead-lbl">{lp_who}</div>
      <div class="ws-lead-pts" style="color:{lp_color}">{lp_pts_str}</div>
    </div>
    <div class="ws-player ws-player-z">
      <div class="ws-name ws-name-z">★ ZOE · 手動輸入</div>
      <div class="ws-score">{z_total}<span class="ws-unit"> pts</span></div>
      <div class="ws-pct" style="color:#E3B341">{z_pct}% 本週份額</div>
    </div>
  </div>
  <!-- Tug-of-war battle bar -->
  <div class="bb-wrap">
    <div class="bb-track" style="background:rgba(48,54,61,0.5)">
      <div class="bb-r" style="width:{r_pct}%"></div>
      <div class="bb-z" style="width:{z_pct}%"></div>
      <div class="bb-mid-line"></div>
    </div>
    <div class="bb-labels">
      <span style="color:#58A6FF">⚡ {r_pct}%</span>
      <span style="font-size:10px;color:rgba(139,148,158,0.5)">｜ 50% 均衡點 ｜</span>
      <span style="color:#E3B341">{z_pct}% ★</span>
    </div>
  </div>
  <!-- Zone 2 pace visual bars -->
  <div class="pv">
    <div class="pv-title">Zone 2 配速對比 <span style="font-weight:400;opacity:0.6">min/km · 條越短越快</span></div>
    <div class="pv-row">
      <div class="pv-name" style="color:#58A6FF">⚡ Randall</div>
      <div class="pv-track">
        <div class="pv-fill" style="width:{r_bar}%;background:#58A6FF"></div>
      </div>
      <div class="pv-val" style="color:#58A6FF">{r_pace}</div>
      <span class="dl {r_pace_dl}">{r_pace_tag}</span>
    </div>
    <div class="pv-row">
      <div class="pv-name" style="color:#E3B341">★ Zoe</div>
      <div class="pv-track">
        <div class="pv-fill" style="width:{z_bar}%;background:#E3B341"></div>
      </div>
      <div class="pv-val" style="color:#E3B341">{z_pace}</div>
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
        ("⚡ Randall", "Randall 負荷", "#58A6FF", "rgba(88,166,255,0.10)"),
        ("★ Zoe",     "Zoe 負荷",    "#E3B341", "rgba(227,179,65,0.08)"),
    ]:
        fig.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=name, mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.6),
            marker=dict(size=6, color=color, line=dict(width=1.5, color="#161B22")),
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
        <div class="cc-stat-val" style="color:#58A6FF">{r_total}</div>
        <div class="cc-stat-lbl">⚡ Randall 本週</div>
      </div>
      <div class="cc-stat">
        <div class="cc-stat-val" style="color:#E3B341">{z_total}</div>
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
        ("⚡ Randall", "Randall 配速", "#58A6FF", "rgba(88,166,255,0.10)"),
        ("★ Zoe",     "Zoe 配速",    "#E3B341", "rgba(227,179,65,0.08)"),
    ]:
        fig2.add_trace(go.Scatter(
            x=df_sim["日期"], y=df_sim[col], name=name, mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.6),
            marker=dict(size=6, color=color, line=dict(width=1.5, color="#161B22")),
            fill="tozeroy", fillcolor=fill,
            hovertemplate="%{y} min/km",
        ))
    fig2.update_layout(**chart_base(reverse_y=True), height=220)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(f"""
    <div class="cc-stats">
      <div class="cc-stat">
        <div class="cc-stat-val" style="color:#58A6FF">{r_pace}</div>
        <div class="cc-stat-lbl">⚡ Randall 平均</div>
      </div>
      <div class="cc-stat">
        <div class="cc-stat-val" style="color:#E3B341">{z_pace}</div>
        <div class="cc-stat-lbl">★ Zoe 平均</div>
      </div>
      <div class="cc-stat">
        <div class="cc-stat-val"><span class="dl {pace_dl}">{pace_sign}{pace_diff}</span></div>
        <div class="cc-stat-lbl">差距 (min/km)</div>
      </div>
    </div>""", unsafe_allow_html=True)

# Cumulative load chart — full width
st.markdown('<div class="cc" style="margin-top:12px"><div class="cc-title">累積訓練量趨勢</div><div class="cc-sub">Cumulative Load · 過去 7 天 <span class="sim">⚠ 模擬</span></div>', unsafe_allow_html=True)
fig_cum = go.Figure()
for _name, _y, _color, _fill in [
    ("⚡ Randall", r_cum, "#58A6FF", "rgba(88,166,255,0.10)"),
    ("★ Zoe",     z_cum, "#E3B341", "rgba(227,179,65,0.08)"),
]:
    fig_cum.add_trace(go.Scatter(
        x=df_sim["日期"], y=_y, name=_name, mode="lines+markers",
        line=dict(color=_color, width=2.5, shape="spline", smoothing=0.6),
        marker=dict(size=6, color=_color, line=dict(width=1.5, color="#161B22")),
        fill="tozeroy", fillcolor=_fill,
        hovertemplate="%{y} pts",
    ))
fig_cum.update_layout(**chart_base(), height=190)
st.plotly_chart(fig_cum, use_container_width=True)
st.markdown(f"""
<div class="cc-stats">
  <div class="cc-stat">
    <div class="cc-stat-val" style="color:#58A6FF">{r_cum[-1]}</div>
    <div class="cc-stat-lbl">⚡ Randall 7 天累積</div>
  </div>
  <div class="cc-stat">
    <div class="cc-stat-val" style="color:#E3B341">{z_cum[-1]}</div>
    <div class="cc-stat-lbl">★ Zoe 7 天累積</div>
  </div>
  <div class="cc-stat">
    <div class="cc-stat-val"><span class="dl {"dl-r" if r_cum[-1] >= z_cum[-1] else "dl-z"}">{("+" if r_cum[-1] >= z_cum[-1] else "") + str(r_cum[-1]-z_cum[-1])}</span></div>
    <div class="cc-stat-lbl">累積差距</div>
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
        <div class="eq-ico" style="background:rgba(227,179,65,0.12)">🏋️</div>
        <div>
          <div class="eq-lbl">Sled Push</div>
          <div class="eq-val">102 kg</div>
          <div class="eq-foot">
            <span class="sb sb-ok">✓ 達標</span>
            <span style="font-size:11px;color:#8B949E">標準 102 kg</span>
          </div>
        </div>
      </div>
      <div class="progtrack">
        <div class="progfill" style="width:100%;background:#E3B341"></div>
      </div>
      <div class="gap-row">
        <div class="gap-item">
          <div class="gap-who" style="color:#58A6FF">⚡ Randall</div>
          <div class="gap-val">102 kg</div>
          <div class="gap-sub">上次測試</div>
        </div>
        <div class="gap-item">
          <div class="gap-who" style="color:#E3B341">★ Zoe</div>
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
        <div class="eq-ico" style="background:rgba(248,81,73,0.12)">🎯</div>
        <div>
          <div class="eq-lbl">Wall Balls · 4 kg</div>
          <div class="eq-val">{wb_cur} <span style="font-size:16px;color:#8B949E">/ {wb_tgt}</span></div>
          <div class="eq-foot">
            <span class="sb sb-bad">差 {wb_gap} 下</span>
            <span style="font-size:11px;color:#8B949E">{wb_pct}% 達標</span>
          </div>
        </div>
      </div>
      <div class="progtrack">
        <div class="progfill" style="width:{wb_pct}%;background:#F85149"></div>
      </div>
      <div class="gap-row">
        <div class="gap-item">
          <div class="gap-who" style="color:#58A6FF">⚡ Randall</div>
          <div class="gap-val">{wb_cur} 下</div>
          <div class="gap-sub">最新測試</div>
        </div>
        <div class="gap-item">
          <div class="gap-who" style="color:#E3B341">★ Zoe</div>
          <div class="gap-val">— 下</div>
          <div class="gap-sub">待測試</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# Equipment readiness bar chart — full width
st.markdown('<div class="cc" style="margin-top:16px"><div class="cc-title">器材達標率對比</div><div class="cc-sub">相對 Women\'s Doubles 官方標準 100% <span class="sim">⚠ Zoe 模擬</span></div>', unsafe_allow_html=True)
_eq_items   = ["Sled Push (102 kg)", "Wall Balls (75 下)"]
_r_scores   = [100, wb_pct]
_z_scores   = [103, 50]
fig_eq = go.Figure()
fig_eq.add_trace(go.Bar(
    name="⚡ Randall", x=_eq_items, y=_r_scores,
    marker=dict(color="#58A6FF", opacity=0.82, line=dict(width=0)),
    text=[f"{v}%" for v in _r_scores], textposition="outside",
    textfont=dict(color="#58A6FF", size=11),
))
fig_eq.add_trace(go.Bar(
    name="★ Zoe", x=_eq_items, y=_z_scores,
    marker=dict(color="#E3B341", opacity=0.82, line=dict(width=0)),
    text=[f"{v}%" for v in _z_scores], textposition="outside",
    textfont=dict(color="#E3B341", size=11),
))
_eq_layout = chart_base()
_eq_layout["barmode"] = "group"
_eq_layout["yaxis"]["range"] = [0, 130]
_eq_layout["height"] = 200
fig_eq.update_layout(**_eq_layout)
fig_eq.add_shape(type="line", x0=-0.5, x1=1.5, y0=100, y1=100,
                  line=dict(color="rgba(227,179,65,0.55)", width=1.5, dash="dash"))
fig_eq.add_annotation(x=1.5, y=100, text="目標 100%", showarrow=False,
                       xanchor="left", font=dict(color="#E3B341", size=10))
st.plotly_chart(fig_eq, use_container_width=True)

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
    ("recovery","恢復狀態","#58A6FF","rgba(88,166,255,0.10)",
     health["recovery"], r_cls, r_lbl, health["recovery_level"] or "COROS"),
    ("sleep","睡眠評分","#E3B341","rgba(227,179,65,0.10)",
     health["sleep_score"], s_cls, s_lbl, health["sleep_dur"] or "今晚"),
    ("hr","靜止心率","#79C0FF","rgba(121,192,255,0.10)",
     health["hr"]+" bpm" if health["hr"]!="—" else "—", h_cls, h_lbl, "今日"),
    ("stress","壓力指數","#E3B341","rgba(227,179,65,0.10)",
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

# Bio radar chart
_bio_rec = int(health["recovery"].replace("%","")) if "%" in str(health["recovery"]) else 50
_bio_slp = int(health["sleep_score"]) if health["sleep_score"] not in ("—","") else 50
_hr_raw  = int(health["hr"]) if health["hr"] not in ("—","") else 60
_bio_hr  = max(0, min(100, round((80 - _hr_raw) / 40 * 100)))  # 40bpm=100%, 80bpm=0%
_st_raw  = int(health["stress"]) if health["stress"] not in ("—","") else 50
_bio_st  = max(0, min(100, round((100 - _st_raw))))             # 0 stress=100%, 100=0%

_radar_cats = ["恢復力", "睡眠品質", "靜止心率", "抗壓性"]
_radar_vals = [_bio_rec, _bio_slp, _bio_hr, _bio_st]

bio_r_col, bio_desc_col = st.columns([1, 1])
with bio_r_col:
    fig_rd = go.Figure()
    fig_rd.add_trace(go.Scatterpolar(
        r=_radar_vals + [_radar_vals[0]],
        theta=_radar_cats + [_radar_cats[0]],
        fill="toself",
        fillcolor="rgba(88,166,255,0.12)",
        line=dict(color="#58A6FF", width=2.5),
        name="Randall",
        hovertemplate="%{theta}: %{r}",
    ))
    fig_rd.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 100], showticklabels=False,
                gridcolor="rgba(48,54,61,0.6)", linecolor="rgba(48,54,61,0.6)",
            ),
            angularaxis=dict(
                tickfont=dict(color="#8B949E", size=12),
                gridcolor="rgba(48,54,61,0.6)", linecolor="rgba(48,54,61,0.7)",
            ),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1,
                    font=dict(size=11, color="#8B949E"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=20, r=20, t=36, b=20),
        font=dict(family="Roboto,system-ui", color="#8B949E", size=11),
        hoverlabel=dict(bgcolor="#1C2128", bordercolor="rgba(48,54,61,0.8)",
                        font=dict(color="#E6EDF3", size=12)),
        height=270,
    )
    st.plotly_chart(fig_rd, use_container_width=True)

with bio_desc_col:
    _bio_overall = round(sum(_radar_vals) / len(_radar_vals))
    _bio_grade   = ("sb-ok","優良") if _bio_overall >= 70 else ("sb-med","普通") if _bio_overall >= 50 else ("sb-bad","偏弱")
    st.markdown(f"""
    <div style="padding:16px 8px">
      <div style="font-size:10px;font-weight:500;letter-spacing:1px;text-transform:uppercase;color:#8B949E;margin-bottom:12px">生物指標總覽</div>
      {''.join([f'<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(48,54,61,0.4)"><span style="font-size:12px;color:#8B949E">{c}</span><div style="display:flex;align-items:center;gap:8px"><div style="width:60px;height:5px;border-radius:3px;background:rgba(48,54,61,0.4);overflow:hidden"><div style="width:{v}%;height:100%;background:#58A6FF;border-radius:3px"></div></div><span style="font-family:\'Roboto Mono\',monospace;font-size:13px;color:#58A6FF;width:28px;text-align:right">{v}</span></div></div>' for c,v in zip(_radar_cats,_radar_vals)])}
      <div style="margin-top:14px;display:flex;align-items:center;gap:10px">
        <span style="font-family:\'Roboto Mono\',monospace;font-size:30px;color:#58A6FF;font-weight:400">{_bio_overall}</span>
        <div><span class="sb {_bio_grade[0]}" style="display:inline-block;margin-bottom:4px">{_bio_grade[1]}</span><div style="font-size:10px;color:rgba(139,148,158,0.6)">綜合生物指數 / 100</div></div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── 6b  ZOE · 訓練數據 ────────────────────────────────────────────────────────
st.markdown("""
<div class="sh">
  <div class="sh-tag">ZOE · 訓練數據</div>
  <div class="sh-title">★ Zoe 的訓練數據</div>
  <div class="sh-sub">每日手動輸入 · 7 天滾動統計</div>
</div>
""", unsafe_allow_html=True)

if _zoe_has_real:
    _src_badge = "✓ 手動輸入" if _zoe_is_manual else "✓ 真實數據"
    _src_color = "#E3B341"
    _src_label = f"Zoe · {_zoe_source_lbl}"
    _src_meta  = f"最後更新：{zoe['updated']}"
    st.markdown(f"""
    <div class="sc">
      <div class="sc-row">
        <div class="sc-avatar" style="background:var(--z-bg)">★</div>
        <div>
          <div class="sc-name" style="color:{_src_color}">{_src_label}</div>
          <div class="sc-meta">{_src_meta}</div>
        </div>
        <span class="sb sb-ok" style="margin-left:auto">{_src_badge}</span>
      </div>
      <div class="sc-stat-row">
        <div class="sc-stat">
          <div class="sc-stat-val" style="color:#E3B341">{zoe['count']}</div>
          <div class="sc-stat-lbl">近 7 天活動</div>
        </div>
        <div class="sc-stat">
          <div class="sc-stat-val" style="color:#E3B341">{zoe['total_load']}</div>
          <div class="sc-stat-lbl">7 天總負荷</div>
        </div>
        <div class="sc-stat">
          <div class="sc-stat-val">{zoe['total_km']} km</div>
          <div class="sc-stat-lbl">7 天總距離</div>
        </div>
        <div class="sc-stat">
          <div class="sc-stat-val">{zoe['avg_pace']}</div>
          <div class="sc-stat-lbl">平均配速</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    if zoe["activities"]:
        with st.expander("★ Zoe 近期活動明細", expanded=False):
            _rows = ""
            for _a in zoe["activities"][:6]:
                _km = f"{_a.get('distance_km', '—')} km" if _a.get("distance_km") else "—"
                _hr = f"{_a['avg_hr']} bpm" if _a.get("avg_hr") else "—"
                _rows += f"""<tr>
                  <td style="color:#8B949E;font-size:12px">{_a.get('date','')}</td>
                  <td><span style="color:#E3B341;font-weight:500">{str(_a.get('name',''))[:20]}</span></td>
                  <td><span style="color:#8B949E;font-size:12px">{_a.get('sport','')}</span></td>
                  <td>{_km}</td>
                  <td>{_a.get('avg_pace','—')}</td>
                  <td>{_hr}</td>
                  <td style="color:#E3B341">{_a.get('training_load','—')}</td>
                </tr>"""
            st.markdown(f"""
            <table class="at">
              <thead><tr>
                <th>日期</th><th>名稱</th><th>項目</th>
                <th>距離</th><th>配速</th><th>心率</th><th>負荷</th>
              </tr></thead>
              <tbody>{_rows}</tbody>
            </table>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="sc">
      <div class="sc-row">
        <div class="sc-avatar" style="background:var(--z-bg)">★</div>
        <div>
          <div class="sc-name">Zoe 尚未輸入訓練資料</div>
          <div class="sc-meta">使用下方表單新增第一筆訓練，統計數據就會顯示</div>
        </div>
        <span class="sb sb-med" style="margin-left:auto">尚無資料</span>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Zoe 手動輸入表單 ────────────────────────────────────────────────────────────
with st.expander("★ Zoe · 新增訓練記錄", expanded=not _zoe_has_real):
    with st.form("zoe_input_form", clear_on_submit=True):
        _col1, _col2 = st.columns(2)
        with _col1:
            _fi_date  = st.date_input("日期", value=datetime.today())
            _fi_name  = st.text_input("名稱", placeholder="例：晨跑、午間跑步")
            _fi_sport = st.selectbox("運動類型", ["Run","Strength","Cycling","Swimming","Walk","Other"])
            _fi_load  = st.number_input("訓練負荷", min_value=0, max_value=500, value=60, step=1)
        with _col2:
            _fi_km    = st.number_input("距離（km）", min_value=0.0, max_value=200.0, value=0.0, step=0.1)
            _fi_pace  = st.text_input("平均配速（mm:ss）", placeholder="例：5:30")
            _fi_hr    = st.number_input("平均心率（bpm，0 = 略過）", min_value=0, max_value=250, value=0, step=1)
        _submit = st.form_submit_button("儲存訓練")

    if _submit:
        _pace_f = _pace_to_float(_fi_pace) if _fi_pace.strip() else None
        _new_act = {
            "date":           _fi_date.strftime("%Y-%m-%d"),
            "name":           _fi_name or _fi_sport,
            "sport":          _fi_sport,
            "training_load":  int(_fi_load),
            "distance_km":    float(_fi_km) if _fi_km > 0 else None,
            "avg_pace":       _fi_pace.strip() if _fi_pace.strip() else "—",
            "avg_pace_float": _pace_f,
            "avg_hr":         int(_fi_hr) if _fi_hr > 0 else None,
        }
        with st.spinner("儲存中..."):
            _ok, _msg = write_zoe_activity(_new_act)
        if _ok:
            st.success(_msg + " 請稍候幾秒後重新整理頁面。")
        else:
            st.error(_msg)

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
              <td style="color:#8B949E;font-size:12px">{a['date']}</td>
              <td><span style="color:#E6EDF3;font-weight:500">{a['name']}</span>
                  <span style="color:#8B949E;font-size:12px;margin-left:6px">· {sport_short}</span></td>
              <td><span class="al {lcls}">{lbl}</span></td>
              <td>{a['dur']}</td><td>{a['hr']}</td>
              <td style="color:#8B949E">{a['cal']}</td></tr>"""
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
