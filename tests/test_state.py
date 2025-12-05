from padel_tournament.core.state import TournamentState


def test_tournament_state_serialization_roundtrip():
    state = TournamentState(
        names=["A", "B", "C", "D"],
        team_size=2,
        num_courts=2,
        matches=[[("A", "B"), ("C", "D")]],
    )
    scores = [
        {"team_one": "A|B", "team_two": "C|D", "score_one": 6, "score_two": 3}
    ]

    payload = state.to_payload(scores)
    restored_state, restored_scores = TournamentState.from_payload(payload)

    assert restored_state == state
    assert restored_scores == scores


def test_tournament_state_from_payload_defaults_missing_fields():
    payload = {"names": ["A"], "matches": [[("A",)]]}
    state, scores = TournamentState.from_payload(payload)

    assert state.team_size == 2
    assert state.num_courts == 1
    assert scores == []


def test_tournament_state_to_payload_returns_copies():
    state = TournamentState(
        names=["A", "B"],
        matches=[[("A", "B"), ("C", "D")]],
    )
    payload = state.to_payload([])

    payload["names"].append("Z")
    payload["matches"][0][0][0] = "X"

    assert state.names == ["A", "B"]
    assert state.matches == [[("A", "B"), ("C", "D")]]


def test_tournament_state_handles_large_rosters():
    names = [f"Player {idx}" for idx in range(1, 41)]
    matches = []
    for offset in range(0, len(names), 4):
        chunk = names[offset:offset + 4]
        if len(chunk) < 4:
            break
        matches.append([(chunk[0], chunk[1]), (chunk[2], chunk[3])])

    state = TournamentState(names=names, team_size=2, num_courts=4, matches=matches)
    scores = [
        {
            "team_one": "|".join(team[0]),
            "team_two": "|".join(team[1]),
            "score_one": idx + 5,
            "score_two": idx,
        }
        for idx, team in enumerate(matches)
    ]

    payload = state.to_payload(scores)
    restored_state, restored_scores = TournamentState.from_payload(payload)

    assert restored_state.names == names
    assert len(restored_state.matches) == len(matches)
    assert restored_scores == scores
