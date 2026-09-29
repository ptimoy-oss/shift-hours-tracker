from flask import Flask, render_template, request, jsonify
import json
from pathlib import Path
from datetime import datetime, timedelta

app = Flask(__name__)

DATA_FILE = Path("data") / "shifts.json"
DATA_FILE.parent.mkdir(exist_ok=True)

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def default_week_data():
    return {
        day: {
            "start": "",
            "end": "",
            "break_minutes": 0,
            "notes": "",
        }
        for day in DAYS
    }


def load_data():
    if not DATA_FILE.exists():
        save_data(default_week_data())

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = default_week_data()
        save_data(data)

    week = default_week_data()
    for day in DAYS:
        if day in data:
            week[day] = {**week[day], **data[day]}
    return week


def save_data(data):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def compute_shift_hours(start_str, end_str, break_minutes):
    if not start_str or not end_str:
        return 0.0

    try:
        start = datetime.strptime(start_str, "%H:%M")
        end = datetime.strptime(end_str, "%H:%M")
        if end <= start:
            end += timedelta(days=1)

        delta = end - start
        hours = delta.total_seconds() / 3600
        hours -= (int(break_minutes) or 0) / 60
        return round(max(hours, 0), 2)
    except ValueError:
        return 0.0


def compute_week_total(data):
    total = 0.0
    for day in DAYS:
        day_data = data.get(day, {})
        total += compute_shift_hours(
            day_data.get("start", ""),
            day_data.get("end", ""),
            day_data.get("break_minutes", 0),
        )
    return round(total, 2)


@app.route("/")
def index():
    data = load_data()
    totals = {}
    for day in DAYS:
        day_data = data.get(day, {})
        totals[day] = compute_shift_hours(
            day_data.get("start", ""),
            day_data.get("end", ""),
            day_data.get("break_minutes", 0),
        )

    weekly_total = compute_week_total(data)
    return render_template("index.html", days=DAYS, data=data, totals=totals, weekly_total=weekly_total)


@app.route("/save", methods=["POST"])
def save():
    payload = request.get_json(force=True)
    data = default_week_data()

    for day in DAYS:
        if day in payload:
            entry = payload[day]
            data[day] = {
                "start": entry.get("start", ""),
                "end": entry.get("end", ""),
                "break_minutes": int(entry.get("break_minutes", 0) or 0),
                "notes": entry.get("notes", ""),
            }

    save_data(data)
    return jsonify({"success": True, "weekly_total": compute_week_total(data)})


if __name__ == "__main__":
    app.run(debug=True)
