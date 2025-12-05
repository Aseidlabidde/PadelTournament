from padel_tournament.core.scheduler import generate_schedule


def test_generate_schedule_balances_players():
    names = [f"Player {i}" for i in range(1, 5)]
    schedule = generate_schedule(names, team_size=2, num_courts=1)
    assert schedule, "Expected at least one match"
    first_match = schedule[0]
    # Ensure each court has two teams of the requested size
    assert len(first_match) == 2
    for team in first_match:
        assert len(team) == 2
        assert set(team).issubset(set(names))


def test_generate_schedule_requires_enough_players():
    schedule = generate_schedule(["A", "B", "C"], team_size=2, num_courts=1)
    assert schedule == []


def test_generate_schedule_deduplicates_names():
    names = ["A", "B", "A", "C", "D"]
    schedule = generate_schedule(names, team_size=2, num_courts=1)
    flat_players = {player for match in schedule for team in match for player in team}
    assert flat_players == {"A", "B", "C", "D"}


def test_generate_schedule_validates_parameters():
    assert generate_schedule(["A", "B", "C", "D"], team_size=1, num_courts=1) == []
    assert generate_schedule(["A", "B", "C", "D"], team_size=2, num_courts=0) == []


def test_generate_schedule_avoids_player_overlap_per_match():
    names = [f"Player {idx}" for idx in range(1, 9)]
    schedule = generate_schedule(names, team_size=2, num_courts=2)
    for match in schedule:
        seen = set()
        for team in match:
            for player in team:
                assert player not in seen
                seen.add(player)


def test_generate_schedule_covers_all_unique_teams_for_full_courts():
    names = [f"Player {idx}" for idx in range(1, 9)]
    schedule = generate_schedule(names, team_size=2, num_courts=2)
    assert schedule, "Expected schedule to be generated"

    unique_teams = {tuple(sorted(team)) for match in schedule for team in match}
    assert len(unique_teams) == 28  # comb(8, 2)

    for match in schedule:
        assert len(match) == 4  # two courts -> four teams per round
        assert {player for team in match for player in team} == set(names)


def test_generate_schedule_scales_with_large_roster():
    names = [f"Player {idx}" for idx in range(1, 33)]
    schedule = generate_schedule(names, team_size=2, num_courts=4)
    assert schedule, "Large roster should still produce schedule"

    players_seen = set()
    for match in schedule:
        assert len(match) <= 8
        assert len(match) % 2 == 0
        seen = set()
        for team in match:
            assert len(team) == 2
            for player in team:
                assert player not in seen
                seen.add(player)
        players_seen.update(seen)
        assert len(seen) == len(match) * 2

    assert players_seen == set(names)
