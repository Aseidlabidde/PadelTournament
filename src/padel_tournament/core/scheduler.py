"""Scheduling utilities for generating fair padel match rotations."""
from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from typing import Iterable, Sequence


def generate_schedule(names: Sequence[str], team_size: int, num_courts: int) -> list[list[tuple[str, ...]]]:
    """Return one valid schedule (list of matches) or an empty list.

    The algorithm pairs every possible team (combination of players) exactly once and
    groups disjoint teams into match slots. When the roster is larger than the courts
    can host, surplus players simply sit out that slot.
    """

    if team_size < 2 or num_courts < 1:
        return []

    players = list(dict.fromkeys(names))  # keep input order, drop duplicates
    if len(players) < team_size * 2:
        return []

    teams = [tuple(team) for team in combinations(players, team_size)]
    if not teams:
        return []

    teams_per_match = num_courts * 2
    if teams_per_match == 0:
        return []

    team_player_sets = [set(team) for team in teams]
    disjoint_sets = tuple(
        frozenset(
            idx
            for idx, candidate in enumerate(team_player_sets)
            if idx != team_index and candidate.isdisjoint(team_player_sets[team_index])
        )
        for team_index in range(len(teams))
    )

    def candidate_order(iterable: Iterable[int], available: set[int]) -> list[int]:
        return sorted(iterable, key=lambda idx: len(disjoint_sets[idx] & available))

    def generate_matches(first_idx: int, remaining_set: set[int]):
        used_players = set(team_player_sets[first_idx])
        available = remaining_set - {first_idx}
        opponents = candidate_order(disjoint_sets[first_idx] & available, available)
        for opponent in opponents:
            if not team_player_sets[opponent].isdisjoint(used_players):
                continue
            match = (first_idx, opponent)
            used_with_opponent = used_players | team_player_sets[opponent]
            next_available = available - {opponent}
            yield from fill_remaining_courts(match, used_with_opponent, next_available, 1)

    def fill_remaining_courts(
        match_prefix: tuple[int, ...],
        used_players: set[str],
        available: set[int],
        court_index: int,
    ):
        if court_index >= num_courts or len(available) < 2:
            yield match_prefix, available
            return

        ordered_candidates = candidate_order(available, available)
        produced = False
        for team_a in ordered_candidates:
            if not team_player_sets[team_a].isdisjoint(used_players):
                continue
            used_with_a = used_players | team_player_sets[team_a]
            remaining_after_a = available - {team_a}
            opponents = candidate_order(disjoint_sets[team_a] & remaining_after_a, remaining_after_a)
            for team_b in opponents:
                if not team_player_sets[team_b].isdisjoint(used_with_a):
                    continue
                new_used = used_with_a | team_player_sets[team_b]
                new_available = remaining_after_a - {team_b}
                produced = True
                yield from fill_remaining_courts(
                    match_prefix + (team_a, team_b),
                    new_used,
                    new_available,
                    court_index + 1,
                )
        if not produced:
            yield match_prefix, available

    @lru_cache(maxsize=None)
    def backtrack(remaining: tuple[int, ...]) -> tuple[tuple[int, ...], ...] | None:
        if not remaining:
            return tuple()
        remaining_set = set(remaining)
        anchor = min(remaining_set, key=lambda idx: len(disjoint_sets[idx] & remaining_set))
        for match, leftover in generate_matches(anchor, remaining_set):
            result = backtrack(tuple(sorted(leftover)))
            if result is not None:
                return (match,) + result
        return None

    initial_state = tuple(range(len(teams)))
    matched = backtrack(initial_state)
    if matched is None:
        return []

    schedule: list[list[tuple[str, ...]]] = []
    for match in matched:
        schedule.append([teams[idx] for idx in match])
    return schedule
