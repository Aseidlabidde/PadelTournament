"""Domain model for tournament configuration and progress."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence


@dataclass(slots=True)
class TournamentState:
    """Serializable snapshot of the tournament setup and scores."""

    names: List[str] = field(default_factory=list)
    team_size: int = 2
    num_courts: int = 1
    matches: List[List[tuple[str, ...]]] = field(default_factory=list)
    history: List[Dict[str, int]] = field(default_factory=list)

    def to_payload(self, scores: Sequence[dict[str, object]]) -> dict[str, object]:
        return {
            "names": list(self.names),
            "team_size": self.team_size,
            "num_courts": self.num_courts,
            "matches": [[list(team) for team in match] for match in self.matches],
            "scores": list(scores),
        }

    @classmethod
    def from_payload(
        cls,
        payload: dict[str, object],
    ) -> tuple["TournamentState", list[dict[str, object]]]:
        matches = [
            [tuple(team) for team in match]
            for match in payload.get("matches", [])
        ]
        state = cls(
            names=list(payload.get("names", [])),
            team_size=int(payload.get("team_size", 2)),
            num_courts=int(payload.get("num_courts", 1)),
            matches=matches,
        )
        scores = list(payload.get("scores", []))
        return state, scores
