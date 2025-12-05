"""Persistence helpers for saving, loading, and exporting tournaments."""
from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path
from typing import Iterable, Sequence

from PyQt6.QtGui import QFont, QPdfWriter, QTextDocument

from ..core.state import TournamentState

ScoreTuple = tuple[tuple[str, ...], tuple[str, ...], str, str]

__all__ = [
    "load_payload",
    "save_payload",
    "export_csv",
    "export_pdf",
]


def load_payload(file_path: str | Path) -> tuple[TournamentState, list[dict[str, object]]]:
    """Read a tournament payload from disk."""

    with open(file_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return TournamentState.from_payload(payload)


def save_payload(file_path: str | Path, state: TournamentState, scores: Sequence[dict[str, object]]) -> None:
    """Persist the tournament state and scores to disk."""

    payload = state.to_payload(scores)
    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def export_csv(
    file_path: str | Path,
    matches: Sequence[Sequence[tuple[str, ...]]],
    rankings: Sequence[tuple[int, str, int, int, int]],
    scores: Iterable[ScoreTuple],
) -> None:
    """Write matches and rankings to a CSV file."""

    score_list = list(scores)
    with open(file_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Match", "Game", "Team1", "Team2", "Score1", "Score2"])
        score_index = 0
        for match_index, match in enumerate(matches, start=1):
            for game_index in range(0, len(match), 2):
                try:
                    team_one, team_two, score_one, score_two = score_list[score_index]
                except IndexError:
                    team_one = match[game_index]
                    team_two = match[game_index + 1]
                    score_one = score_two = ""
                writer.writerow(
                    [
                        match_index,
                        game_index // 2 + 1,
                        "|".join(team_one),
                        "|".join(team_two),
                        score_one,
                        score_two,
                    ]
                )
                score_index += 1
        writer.writerow([])
        writer.writerow(["Place", "Player", "Points", "Wins", "Losses"])
        for place, name, points, wins, losses in rankings:
            writer.writerow([place, name, points, wins, losses])


def export_pdf(
    file_path: str | Path,
    state: TournamentState,
    rankings: Sequence[tuple[int, str, int, int, int]],
    scores: Iterable[ScoreTuple],
) -> None:
    """Render a PDF report summarizing the tournament."""

    pdf = QPdfWriter(str(file_path))
    doc = QTextDocument()
    doc.setDefaultFont(QFont("Segoe UI", 11))

    styles = """
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; color: #1f2933; }
        h1 { font-size: 20pt; margin: 0 0 12px 0; }
        h2 { font-size: 14pt; margin: 18px 0 8px 0; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 12px; }
        th, td { border: 1px solid #d0d7e2; padding: 6px 8px; text-align: center; }
        th { background-color: #e2e8f0; }
        .meta { margin-bottom: 16px; }
        .meta div { margin-bottom: 4px; }
    </style>
    """

    html_parts: list[str] = [
        "<html><head>",
        styles,
        "</head><body>",
        "<h1>Padel Tournament Report</h1>",
        "<div class='meta'>",
        f"<div><strong>Players:</strong> {', '.join(escape(name) for name in state.names)}</div>",
        f"<div><strong>Team size:</strong> {state.team_size}</div>",
        f"<div><strong>Courts:</strong> {state.num_courts}</div>",
        "</div>",
    ]

    def format_team(team: tuple[str, ...]) -> str:
        return " & ".join(escape(player) for player in team)

    score_rows = list(scores)
    html_parts.append("<h2>Schedule & Scores</h2>")
    html_parts.append("<table><thead><tr><th>Match</th><th>Game</th><th>Team 1</th><th>Team 2</th><th>Score</th></tr></thead><tbody>")
    score_index = 0
    for match_index, match in enumerate(state.matches, start=1):
        for game_index in range(0, len(match), 2):
            try:
                team_one, team_two, score_one, score_two = score_rows[score_index]
            except IndexError:
                team_one = match[game_index]
                team_two = match[game_index + 1]
                score_one = score_two = ""
            html_parts.append(
                "<tr>"
                f"<td>{match_index}</td>"
                f"<td>{game_index // 2 + 1}</td>"
                f"<td>{format_team(team_one)}</td>"
                f"<td>{format_team(team_two)}</td>"
                f"<td>{escape(str(score_one))} - {escape(str(score_two))}</td>"
                "</tr>"
            )
            score_index += 1
    html_parts.append("</tbody></table>")

    html_parts.append("<h2>Rankings</h2>")
    html_parts.append("<table><thead><tr><th>Place</th><th>Player</th><th>Points</th><th>Wins</th><th>Losses</th></tr></thead><tbody>")
    for place, name, points, wins, losses in rankings:
        html_parts.append(
            "<tr>"
            f"<td>{place}</td>"
            f"<td>{escape(name)}</td>"
            f"<td>{points}</td>"
            f"<td>{wins}</td>"
            f"<td>{losses}</td>"
            "</tr>"
        )
    html_parts.append("</tbody></table>")
    html_parts.append("</body></html>")

    doc.setHtml("".join(html_parts))
    doc.print(pdf)
