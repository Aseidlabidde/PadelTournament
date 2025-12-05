# Padel Tournament Manager

A PyQt6 desktop application for planning and tracking padel matches. The UI lets you configure a tournament, enter player names, record scores, and review rankings and performance charts.

## Features
- Responsive PyQt6 interface with light and dark themes
- Automatic schedule generation with support for idle courts
- Score tracking with auto-updated rankings and win/loss records
- Player performance chart powered by Matplotlib
- JSON persistence plus CSV and PDF exports

## Project layout
```
src/
  padel_tournament/
    core/            # Domain logic (state model, scheduler)
    services/        # Ranking calculations and persistence helpers
    themes/          # Packaged QSS themes
    ui/              # Qt widgets including the main window and stacked pages
scripts/
  run_app.py         # Convenience launcher
examples/
  sample_tournament.json
```

## Getting started
1. Create a virtual environment and install dependencies:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -U pip
   pip install -e .
   ```
2. Launch the app:
   ```powershell
   python -m padel_tournament
   ```

## Tests
Run the unit tests with:
```powershell
python -m pytest
```

## License
This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.
