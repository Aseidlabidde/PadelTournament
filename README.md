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
    ui/              # Qt widgets and runtime helpers (main window, pages, widgets)
      designer/      # Source .ui files organised by page/panel
      pages/
        score_builder.py   # Assembles the score page from modular sections
        score_components.py# Matches, rankings, analytics helpers
        score_payload.py    # Serialisation helpers for score state
scripts/
  run_app.py         # Convenience launcher
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

  ## Building a standalone executable

  The repository ships with a `Makefile` that automates the PyInstaller bundle:

  ```powershell
  make build
  ```

  > Requires `make` (available via Git for Windows, MSYS2, or WSL).

  The target will create a `.venv` if needed, install the editable package plus PyInstaller, and then produce the distributable under `dist/PadelTournament/PadelTournament.exe`. Run `make clean` to remove previous build artefacts.

## Development notes

- The score page UI is now composed from a lean container `.ui` file plus a reusable analytics panel. The runtime widgets are wired together via `ScorePageBuilder`, which instantiates dedicated `MatchesSection`, `RankingsSection`, and `AnalyticsSection` helpers. This keeps the generated code small and enables focused unit tests.
- Designer assets live under `src/padel_tournament/ui/designer/`. Run `python -m PyQt6.uic.pyuic <ui-file> -o <target.py>` after editing a `.ui` file to regenerate its Python stub.
- New analytics and plotting utilities are covered by tests in `tests/test_performance_charts.py`.

## Tests
Run the unit tests with:
```powershell
python -m pytest
```

## License
This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.
