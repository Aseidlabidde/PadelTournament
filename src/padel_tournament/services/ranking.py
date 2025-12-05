"""Utilities for computing rankings and score history."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Sequence, Tuple


ScoreTuple = Tuple[tuple[str, ...], tuple[str, ...], str, str]
Match = Sequence[tuple[str, ...]]


@dataclass(slots=True)
class RankingResult:
    """Aggregated ranking data for presentation and exports."""

    rankings: List[tuple[int, str, int, int, int]]
    history: List[Dict[str, int]]
    points: Dict[str, int]
    records: Dict[str, Dict[str, int]]


def compute_rankings(
    matches: Sequence[Match],
    names: Sequence[str],
    scores: Iterable[ScoreTuple],
) -> RankingResult:
    """Compute rankings, history, points, and win/loss records."""

    points: DefaultDict[str, int] = defaultdict(int)
    records: DefaultDict[str, Dict[str, int]] = defaultdict(lambda: {"wins": 0, "losses": 0})
    history: List[Dict[str, int]] = []

    score_iter = iter(scores)
    for match in matches:
        per_match: DefaultDict[str, int] = defaultdict(int)
        for idx in range(0, len(match), 2):
            try:
                team_one, team_two, score_one_text, score_two_text = next(score_iter)
            except StopIteration:
                break

            if not score_one_text or not score_two_text:
                continue
            try:
                score_one = int(score_one_text)
                score_two = int(score_two_text)
            except ValueError:
                continue

            for player in team_one:
                per_match[player] += score_one
            for player in team_two:
                per_match[player] += score_two

            if score_one > score_two:
                for player in team_one:
                    records[player]["wins"] += 1
                for player in team_two:
                    records[player]["losses"] += 1
            elif score_two > score_one:
                for player in team_two:
                    records[player]["wins"] += 1
                for player in team_one:
                    records[player]["losses"] += 1

        for player, total in per_match.items():
            points[player] += total
        if per_match:
            history.append(dict(per_match))
        else:
            history.append({})

    ranked: List[tuple[str, int, int, int]] = []
    for name in names:
        stats = records[name]
        ranked.append((name, points[name], stats["wins"], stats["losses"]))

    ranked.sort(key=lambda item: (-item[1], -item[2], item[3], item[0]))
    rankings = [(index, *entry) for index, entry in enumerate(ranked, start=1)]

    return RankingResult(rankings=rankings, history=history, points=dict(points), records={k: dict(v) for k, v in records.items()})
