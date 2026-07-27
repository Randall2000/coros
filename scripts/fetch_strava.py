"""
GitHub Actions 用：用儲存的 refresh token 自動抓 Zoe 的 Strava 活動。
寫入 data/strava.json，格式與 fetch_intervals.py 相同。

Usage:
    python scripts/fetch_strava.py [output_path]

Required env vars:
    STRAVA_CLIENT_ID
    STRAVA_CLIENT_SECRET
    STRAVA_REFRESH_TOKEN
    STRAVA_ATHLETE_ID   (optional, for display only)
"""
import os, json, sys, requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

CLIENT_ID     = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]
ATHLETE_ID    = os.environ.get("STRAVA_ATHLETE_ID", "")


def get_access_token() -> str:
    r = requests.post("https://www.strava.com/oauth/token", data={
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type":    "refresh_token",
    }, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def pace_str(avg_speed_ms: float) -> str:
    if not avg_speed_ms or avg_speed_ms <= 0:
        return "—"
    s = 1000 / avg_speed_ms
    return f"{int(s // 60)}:{int(s % 60):02d}"


def pace_float(avg_speed_ms: float):
    if not avg_speed_ms or avg_speed_ms <= 0:
        return None
    return round((1000 / avg_speed_ms) / 60, 2)


def fetch() -> dict:
    access_token = get_access_token()
    since_ts = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())

    r = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"after": since_ts, "per_page": 30},
        timeout=15,
    )
    r.raise_for_status()
    raw = r.json()

    activities = []
    speeds     = []

    for a in raw:
        sport = a.get("sport_type") or a.get("type", "")
        if sport not in ("Run", "VirtualRun", "Ride", "VirtualRide",
                         "Walk", "Swim", "Hike", "Rowing"):
            continue

        spd     = a.get("average_speed")
        dur_min = round((a.get("moving_time") or 0) / 60, 1)
        hr      = a.get("average_heartrate")

        # Training load: prefer Strava suffer_score, else estimate from duration
        load = a.get("suffer_score") or 0
        if not load:
            load = round(dur_min * 0.8)

        if spd:
            speeds.append(spd)

        activities.append({
            "date":           a.get("start_date_local", "")[:10],
            "name":           a.get("name", "—"),
            "sport":          sport,
            "distance_km":    round((a.get("distance") or 0) / 1000, 2),
            "duration_min":   dur_min,
            "avg_pace":       pace_str(spd),
            "avg_pace_float": pace_float(spd),
            "avg_hr":         round(hr) if hr else None,
            "training_load":  load,
            "elevation_m":    round(a.get("total_elevation_gain") or 0),
        })

    avg_spd = sum(speeds) / len(speeds) if speeds else None

    return {
        "updatedAt":     datetime.now(timezone.utc).isoformat() + "Z",
        "source":        "strava",
        "athlete_id":    ATHLETE_ID,
        "activities_7d": activities,
        "summary_7d": {
            "total_load":         sum(a["training_load"] for a in activities),
            "avg_pace":           pace_str(avg_spd),
            "avg_pace_float":     pace_float(avg_spd),
            "total_distance_km":  round(sum(a["distance_km"] for a in activities), 1),
            "total_duration_min": round(sum(a["duration_min"] for a in activities), 1),
            "activity_count":     len(activities),
            "atl":                None,
            "ctl":                None,
        },
    }


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/strava.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    data = fetch()
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    n    = len(data["activities_7d"])
    load = data["summary_7d"]["total_load"]
    km   = data["summary_7d"]["total_distance_km"]
    print(f"✓ {n} activities | load {load} | {km} km | written to {out}")
