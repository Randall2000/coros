"""
Fetch Zoe's training data from intervals.icu API.
Writes to data/strava.json (same filename, new source).

Usage:
    python scripts/fetch_intervals.py [output_path]

Required env vars:
    INTERVALS_ATHLETE_ID  — e.g. "i123456"
    INTERVALS_API_KEY     — from intervals.icu Settings → API Key
"""
import json, os, sys, requests
from datetime import datetime, timedelta
from pathlib import Path

ATHLETE_ID = os.environ["INTERVALS_ATHLETE_ID"]
API_KEY    = os.environ["INTERVALS_API_KEY"]
BASE       = "https://intervals.icu/api/v1"
AUTH       = ("API", API_KEY)


def get(path: str, params: dict = None) -> object:
    r = requests.get(f"{BASE}{path}", auth=AUTH, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def pace_str(avg_speed_ms: float) -> str:
    """Convert m/s to min/km string like '6:15'."""
    if not avg_speed_ms or avg_speed_ms <= 0:
        return "—"
    pace_s = 1000 / avg_speed_ms
    return f"{int(pace_s // 60)}:{int(pace_s % 60):02d}"


def pace_float(avg_speed_ms: float) -> float | None:
    """Convert m/s to decimal min/km like 6.25."""
    if not avg_speed_ms or avg_speed_ms <= 0:
        return None
    pace_s = 1000 / avg_speed_ms
    return round(pace_s / 60, 2)


def fetch() -> dict:
    since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    raw   = get(f"/athlete/{ATHLETE_ID}/activities", {"oldest": since})

    activities = []
    speed_vals = []

    for a in raw:
        sport = a.get("type", "")
        # Include cardio sports only (exclude strength/yoga/etc)
        if sport not in ("Run", "VirtualRun", "Ride", "VirtualRide",
                         "Walk", "Swim", "Hike", "Rowing"):
            continue

        spd = a.get("average_speed")
        if spd:
            speed_vals.append(spd)

        activities.append({
            "date":          a.get("start_date_local", "")[:10],
            "name":          a.get("name", "—"),
            "sport":         sport,
            "distance_km":   round((a.get("distance") or 0) / 1000, 2),
            "duration_min":  round((a.get("moving_time") or 0) / 60, 1),
            "avg_pace":      pace_str(spd),
            "avg_pace_float": pace_float(spd),
            "avg_hr":        round(a.get("average_heartrate") or 0) or None,
            "training_load": a.get("icu_training_load") or 0,
            "elevation_m":   round(a.get("total_elevation_gain") or 0),
            "atl":           round(a["icu_atl"], 1) if a.get("icu_atl") else None,
            "ctl":           round(a["icu_ctl"], 1) if a.get("icu_ctl") else None,
        })

    # Summary from most recent activity's fitness values
    latest_atl = next((a["atl"] for a in activities if a.get("atl")), None)
    latest_ctl = next((a["ctl"] for a in activities if a.get("ctl")), None)
    avg_pace_f  = round(sum(pace_float(s) for s in speed_vals) / len(speed_vals), 2) if speed_vals else None

    return {
        "updatedAt":   datetime.utcnow().isoformat() + "Z",
        "source":      "intervals.icu",
        "athlete_id":  ATHLETE_ID,
        "activities_7d": activities,
        "summary_7d": {
            "total_load":         sum(a["training_load"] for a in activities),
            "avg_pace_float":     avg_pace_f,
            "avg_pace":           pace_str(1000 / (avg_pace_f * 60)) if avg_pace_f else "—",
            "total_distance_km":  round(sum(a["distance_km"] for a in activities), 1),
            "total_duration_min": round(sum(a["duration_min"] for a in activities), 1),
            "activity_count":     len(activities),
            "atl":                latest_atl,
            "ctl":                latest_ctl,
        },
    }


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/strava.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    data = fetch()
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    acts = len(data["activities_7d"])
    load = data["summary_7d"]["total_load"]
    print(f"✓ {acts} activities | total load {load} | written to {out}")
