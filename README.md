# F1 Track Viewer

A Python-based Formula 1 replay visualization tool built with `fastf1` and `arcade`.

## Project Overview

This project downloads Formula 1 telemetry data for the 2024 Las Vegas Grand Prix, processes track geometry and driver telemetry, and renders a live race replay with a real-time leaderboard.

### Key Features

- Visualizes the F1 track layout and car positions in a windowed application
- Uses actual F1 telemetry data from `fastf1`
- Supports live time progression and playback speed control
- Displays a sorted leaderboard based on race distance
- Uses custom team colors for clear visual identity

## Skills Demonstrated

- Python GUI development with `arcade`
- Data processing with `pandas` and `numpy`
- Working with external APIs and telemetry data (`fastf1`)
- Real-time animation and rendering
- Project documentation and reproducible setup

## Requirements

- Python 3.8+
- `arcade`
- `fastf1`
- `pandas`
- `numpy`

## Setup

1. Clone or download the repository.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the viewer:

```bash
python f1_track_viewer.py
```

## Usage

- `SPACE` to pause/resume playback
- `RIGHT` arrow to increase playback speed
- `LEFT` arrow to decrease playback speed
- `R` to reset the race timer

## Notes

- The first run downloads F1 session data and caches it in the `cache/` folder.
- The app currently uses the `2024 Las Vegas Grand Prix` race session.

## Why This Project is Resume-Ready

- Demonstrates a real-world data visualization application
- Integrates live sports telemetry data with graphical rendering
- Highlights Python scripting, GUI development, and data engineering skills
- Includes reproducible setup and clear instructions
