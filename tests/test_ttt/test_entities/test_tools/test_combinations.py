from pytest import mark

from ttt.entities.tools.combinations import Combinations


@mark.parametrize(
    ("combinations", "expected_result"),
    [
        (Combinations([]), []),
        (Combinations([1]), []),
        (Combinations([1, 2]), [(1, 2)]),
        (Combinations([1, 2, 3]), [(1, 2), (1, 3), (2, 3)]),
        (
            Combinations([1, 2, 3, 4]),
            [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)],
        ),
        (
            Combinations([1, 2, 3, 4, 5, 6]),
            [
                (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                (2, 3), (2, 4), (2, 5), (2, 6),
                (3, 4), (3, 5), (3, 6),
                (4, 5), (4, 6),
                (5, 6),
            ],
        ),
    ],
)
def test_without_cut(
    combinations: Combinations[int], expected_result: list[tuple[int, int]],
) -> None:
    assert list(combinations) == expected_result


@mark.parametrize(
    ("combinations", "value_to_cut", "expected_result"),
    [
        (Combinations([]), (0, 0), []),
        (Combinations([1]), (0, 0), []),
        (Combinations([1, 2]), (1, 2), [(1, 2)]),
        (Combinations([1, 2, 3]), (1, 3), [(1, 2), (1, 3)]),
        (Combinations([1, 2, 3, 4]), (1, 2), [(1, 2), (3, 4)]),
        (
            Combinations([1, 2, 3, 4]),
            (1, 3),
            [(1, 2), (1, 3), (2, 4)],
        ),
        (
            Combinations([1, 2, 3, 4]),
            (2, 3),
            [(1, 2), (1, 3), (1, 4), (2, 3)],
        ),
        (
            Combinations([1, 2, 3, 4]),
            (2, 4),
            [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4)],
        ),
        (
            Combinations([1, 2, 3, 4]),
            (3, 4),
            [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)],
        ),
        (
            Combinations([1, 2, 3, 4, 5]),
            (2, 4),
            [(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (3, 5)],
        ),
        (
            Combinations([1, 2, 3, 4, 5]),
            (2, 3),
            [(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (4, 5)],
        ),
        (
            Combinations([1, 2, 3, 4, 5, 6]),
            (1, 6),
            [
                (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                (2, 3), (2, 4), (2, 5),
                (3, 4), (3, 5),
                (4, 5),
            ],
        ),
        (
            Combinations([1, 2, 3, 4, 5, 6]),
            (5, 6),
            [
                (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                (2, 3), (2, 4), (2, 5), (2, 6),
                (3, 4), (3, 5), (3, 6),
                (4, 5), (4, 6),
                (5, 6),
            ],
        ),
        (
            Combinations([1, 2, 3, 4, 5, 6]),
            (4, 6),
            [
                (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                (2, 3), (2, 4), (2, 5), (2, 6),
                (3, 4), (3, 5), (3, 6),
                (4, 5), (4, 6),
            ],
        ),
        (
            Combinations([1, 2, 3, 4, 5, 6]),
            (4, 5),
            [
                (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                (2, 3), (2, 4), (2, 5), (2, 6),
                (3, 4), (3, 5), (3, 6),
                (4, 5),
            ],
        ),
        (
            Combinations([1, 2, 3, 4, 5, 6]),
            (2, 5),
            [
                (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                (2, 3), (2, 4), (2, 5),
                (3, 4), (3, 6),
                (4, 6),
            ],
        ),
        (
            Combinations([1, 2, 3, 4, 5, 6]),
            (3, 6),
            [
                (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                (2, 3), (2, 4), (2, 5), (2, 6),
                (3, 4), (3, 5), (3, 6),
                (4, 5),
            ],
        ),
    ],
)
def test_with_cut(
    combinations: Combinations[int],
    value_to_cut: tuple[int, int],
    expected_result: list[tuple[int, int]],
) -> None:
    result = []

    for value in combinations:
        result.append(value)

        if value == value_to_cut:
            combinations.cut()

    assert result == expected_result
