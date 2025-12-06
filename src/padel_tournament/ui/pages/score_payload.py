"""Utilities for transforming match scores to and from payloads."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from PyQt6.QtWidgets import QLineEdit


@dataclass(slots=True)
class ScoreWidgets:
    """Holds references to the score inputs for a match entry."""

    team_one: tuple[str, ...]
    team_two: tuple[str, ...]
    score_one: QLineEdit
    score_two: QLineEdit


class ScorePayloadCodec:
    """Encodes and decodes tournament score payloads."""

    @staticmethod
    def encode(entries: Iterable[ScoreWidgets]) -> list[dict[str, object]]:
        payload: list[dict[str, object]] = []
        for entry in entries:
            payload.append(
                {
                    "team1": list(entry.team_one),
                    "team2": list(entry.team_two),
                    "score1": entry.score_one.text(),
                    "score2": entry.score_two.text(),
                }
            )
        return payload

    @staticmethod
    def apply(entries: Sequence[ScoreWidgets], payload: Sequence[Mapping[str, object]]) -> None:
        for widget_entry, saved in zip(entries, payload):
            widget_entry.score_one.setText(str(saved.get("score1", "")))
            widget_entry.score_two.setText(str(saved.get("score2", "")))

    @staticmethod
    def iter_scores(entries: Iterable[ScoreWidgets]):
        for entry in entries:
            yield (
                entry.team_one,
                entry.team_two,
                entry.score_one.text().strip(),
                entry.score_two.text().strip(),
            )
