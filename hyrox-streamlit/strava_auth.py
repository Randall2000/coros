"""
Strava OAuth 2.0 helper for HYROX War Room.

Token storage: SQLite (same DB as weekly reviews).
Only one row (id=1) is ever written — represents Zoe's credentials.
"""
import requests, time, sqlite3
from pathlib import Path
from urllib.parse import urlencode

_here = Path(__file__).parent

# ── Secrets (injected by Streamlit Cloud / local .streamlit/secrets.toml) ──
def _secret(key: str, fallback: str = "") -> str:
    try:
        import streamlit as st
        return st.secrets[key]
    except Exception:
        return fallback

def _client_id()     -> str: return _secret("strava_client_id")
def _client_secret() -> str: return _secret("strava_client_secret")
def _redirect_uri()  -> str: return _secret("strava_redirect_uri")

# ── SQLite token store ──────────────────────────────────────────────────────
def _db() -> str:
    return str(_here / "hyrox_review.db")

def _ensure_table():
    conn = sqlite3.connect(_db())
    conn.execute("""
        CREATE TABLE IF NOT EXISTS strava_token (
            id            INTEGER PRIMARY KEY CHECK (id = 1),
            access_token  TEXT,
            refresh_token TEXT,
            expires_at    INTEGER,
            athlete_id    INTEGER,
            scope         TEXT,
            updated_at    TEXT DEFAULT (datetime('now'))
        )""")
    conn.commit()
    conn.close()

def _save_token(data: dict):
    _ensure_table()
    athlete_id = None
    if "athlete" in data:
        athlete_id = data["athlete"].get("id")
    conn = sqlite3.connect(_db())
    conn.execute("""
        INSERT INTO strava_token (id, access_token, refresh_token, expires_at, athlete_id, scope, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            access_token  = excluded.access_token,
            refresh_token = excluded.refresh_token,
            expires_at    = excluded.expires_at,
            athlete_id    = COALESCE(excluded.athlete_id, athlete_id),
            scope         = excluded.scope,
            updated_at    = excluded.updated_at
    """, (data.get("access_token"), data.get("refresh_token"),
          data.get("expires_at"), athlete_id, data.get("scope")))
    conn.commit()
    conn.close()

def _load_raw() -> dict | None:
    _ensure_table()
    conn = sqlite3.connect(_db())
    row = conn.execute(
        "SELECT access_token, refresh_token, expires_at, athlete_id, scope, updated_at "
        "FROM strava_token WHERE id=1"
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "access_token":  row[0],
        "refresh_token": row[1],
        "expires_at":    row[2],
        "athlete_id":    row[3],
        "scope":         row[4],
        "updated_at":    row[5],
    }

def revoke_token():
    conn = sqlite3.connect(_db())
    conn.execute("DELETE FROM strava_token WHERE id=1")
    conn.commit()
    conn.close()

# ── OAuth 2.0 core ──────────────────────────────────────────────────────────
def auth_url() -> str:
    return "https://www.strava.com/oauth/authorize?" + urlencode({
        "client_id":       _client_id(),
        "redirect_uri":    _redirect_uri(),
        "response_type":   "code",
        "approval_prompt": "auto",
        "scope":           "activity:read_all",
    })

def exchange_code(code: str) -> dict:
    r = requests.post("https://www.strava.com/oauth/token", data={
        "client_id":     _client_id(),
        "client_secret": _client_secret(),
        "code":          code,
        "grant_type":    "authorization_code",
    }, timeout=10)
    r.raise_for_status()
    data = r.json()
    _save_token(data)
    return data

def get_valid_token() -> dict | None:
    """Return a live access_token, refreshing if expired. None if not authorised."""
    token = _load_raw()
    if not token or not token.get("refresh_token"):
        return None
    expires_at = token.get("expires_at") or 0
    if expires_at > time.time() + 60:
        return token
    # Token expired → refresh silently
    r = requests.post("https://www.strava.com/oauth/token", data={
        "client_id":     _client_id(),
        "client_secret": _client_secret(),
        "refresh_token": token["refresh_token"],
        "grant_type":    "refresh_token",
    }, timeout=10)
    r.raise_for_status()
    new_token = r.json()
    new_token.setdefault("athlete_id", token.get("athlete_id"))
    _save_token(new_token)
    return new_token

# ── Streamlit callback handler (call once at top of app.py) ─────────────────
def handle_oauth_callback() -> bool:
    """
    Detect Strava's redirect, exchange the code, and rerun.
    Returns True if we just completed OAuth (app will rerun before user sees anything).
    """
    import streamlit as st
    error = st.query_params.get("error")
    if error:
        st.query_params.clear()
        st.warning(f"Strava 授權被取消：{error}")
        return False

    code = st.query_params.get("code")
    if code:
        try:
            exchange_code(code)
        except Exception as e:
            st.error(f"Strava 授權失敗：{e}")
            st.query_params.clear()
            return False
        st.query_params.clear()
        st.rerun()   # reload cleanly without ?code= in URL

    return False

# ── Strava API helpers ───────────────────────────────────────────────────────
def fetch_recent_activities(limit: int = 10) -> list[dict]:
    """Fetch recent activities for the authorised athlete."""
    token = get_valid_token()
    if not token:
        return []
    r = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {token['access_token']}"},
        params={"per_page": limit},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()

def fetch_activity_detail(activity_id: int) -> dict:
    token = get_valid_token()
    if not token:
        return {}
    r = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers={"Authorization": f"Bearer {token['access_token']}"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()
