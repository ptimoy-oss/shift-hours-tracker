# Weekly Shift Hours Tracker

A simple Flask web app for tracking shift hours across a Sunday-to-Saturday week.

## Features
- Sunday to Saturday weekly calendar layout
- Enter start time, end time, break time, and optional notes for each day
- Automatic daily and weekly total calculations
- Save weekly data locally in a JSON file
- Clean browser-based interface

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://localhost:5000
```

## Notes
- Data is stored in `data/shifts.json`.
- The app automatically creates the data folder if it does not exist.
