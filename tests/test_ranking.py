from padel_tournament.services.ranking import compute_rankings


def test_compute_rankings_orders_players_by_points_and_wins():
    matches = [
        [("A", "B"), ("C", "D")],
        [("A", "C"), ("B", "D")],
    ]
    scores = [
        (("A", "B"), ("C", "D"), "6", "3"),
        (("A", "C"), ("B", "D"), "4", "6"),
    ]
    result = compute_rankings(matches, ["A", "B", "C", "D"], scores)

    ranking_names = [entry[1] for entry in result.rankings]
    assert ranking_names == ["B", "A", "D", "C"]

    assert result.points == {"A": 10, "B": 12, "C": 7, "D": 9}
    assert result.records["B"] == {"wins": 2, "losses": 0}
    assert result.history == [
        {"A": 6, "B": 6, "C": 3, "D": 3},
        {"A": 4, "C": 4, "B": 6, "D": 6},
    ]


def test_compute_rankings_ignores_invalid_scores():
    matches = [[("A", "B"), ("C", "D")]]
    scores = [(("A", "B"), ("C", "D"), "abc", "1")]

    result = compute_rankings(matches, ["A", "B", "C", "D"], scores)

    assert result.points == {"A": 0, "B": 0, "C": 0, "D": 0}
    assert result.records == {
        "A": {"wins": 0, "losses": 0},
        "B": {"wins": 0, "losses": 0},
        "C": {"wins": 0, "losses": 0},
        "D": {"wins": 0, "losses": 0},
    }
    assert result.history == [{}]


def test_compute_rankings_handles_missing_scores():
    matches = [
        [("A", "B"), ("C", "D")],
        [("A", "C"), ("B", "D")],
    ]
    scores = [(("A", "B"), ("C", "D"), "7", "5")]

    result = compute_rankings(matches, ["A", "B", "C", "D"], scores)

    assert result.history == [
        {"A": 7, "B": 7, "C": 5, "D": 5},
        {},
    ]


def test_compute_rankings_breaks_ties_by_losses_then_name():
    matches = [
        [("A", "B"), ("C", "D")],
        [("A", "C"), ("B", "D")],
        [("A", "D"), ("B", "C")],
    ]
    scores = [
        (("A", "B"), ("C", "D"), "6", "6"),
        (("A", "C"), ("B", "D"), "5", "5"),
        (("A", "D"), ("B", "C"), "4", "4"),
    ]

    result = compute_rankings(matches, ["A", "B", "C", "D"], scores)

    ranking_names = [entry[1] for entry in result.rankings]
    assert ranking_names == sorted(["A", "B", "C", "D"])


def test_compute_rankings_with_many_players():
    names = [f"Player {idx}" for idx in range(1, 13)]
    matches = [
        [(names[0], names[1]), (names[2], names[3])],
        [(names[4], names[5]), (names[6], names[7])],
        [(names[8], names[9]), (names[10], names[11])],
        [(names[0], names[2]), (names[4], names[6])],
        [(names[1], names[3]), (names[5], names[7])],
        [(names[8], names[10]), (names[9], names[11])],
    ]
    scores = [
        ((names[0], names[1]), (names[2], names[3]), "7", "3"),
        ((names[4], names[5]), (names[6], names[7]), "6", "4"),
        ((names[8], names[9]), (names[10], names[11]), "5", "5"),
        ((names[0], names[2]), (names[4], names[6]), "8", "2"),
        ((names[1], names[3]), (names[5], names[7]), "3", "6"),
        ((names[8], names[10]), (names[9], names[11]), "4", "7"),
    ]

    result = compute_rankings(matches, names, scores)

    assert len(result.history) == len(matches)
    top_three = [entry[1] for entry in result.rankings[:3]]
    assert top_three == [names[0], names[5], names[9]]
    assert result.points[names[0]] > result.points[names[5]]
    assert result.points[names[5]] == result.points[names[11]]
