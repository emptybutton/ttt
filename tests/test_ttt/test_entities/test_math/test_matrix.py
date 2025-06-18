from pytest import mark, raises

from ttt.entities.math.matrix import (
    InconsistentMatrixError,
    Matrix,
    MatrixSize,
    matrix_with_size,
)
from ttt.entities.math.vector import Vector


@mark.parametrize(
    ("input_size", "expected_size"),
    [
        ((10, 5), (10, 5)),
        ((1, 1), (1, 1)),
        ((0, 0), (0, 0)),
        ((1, 0), (0, 0)),
        ((0, 1), (0, 1)),
        ((0, -1), (0, 0)),
        ((0, -5), (0, 0)),
        ((-5, 5), (0, 5)),
    ],
)
def test_matrix_with_size(
    input_size: MatrixSize,
    expected_size: MatrixSize,
) -> None:
    matrix = matrix_with_size(input_size, None)

    assert matrix.size() == expected_size


@mark.parametrize(
    "columns",
    [
        [[None, None], [None]],
        [[None], [None, None]],
        [[None], [None], [None], []],
        [[], [None, None], [None, None], []],
        [[], [None, None], [None, None]],
        [[None, None], [None, None], []],
    ],
)
def test_inconsistent_matrix(columns: list[list[None]]) -> None:
    with raises(InconsistentMatrixError):
        Matrix(columns)


@mark.parametrize(
    ("matrix", "vector"),
    [
        (Matrix([[False]]), (0, 0)),
        (Matrix([[False], [False]]), (0, 1)),
        (Matrix([[False, False], [False, False]]), (1, 1)),
        (Matrix([[False, False], [False, False]]), (1, 0)),
    ],
)
def test_set_get(matrix: Matrix[bool], vector: Vector) -> None:
    matrix[vector] = True

    assert matrix[vector]


@mark.parametrize(
    ("matrix", "vector", "result"),
    [
        (Matrix([[1]]), (0, 0), 1),
        (Matrix([[1], [2]]), (0, 1), 2),
        (Matrix([[1, 2], [3, 4]]), (1, 1), 4),
        (Matrix([[1, 2], [3, 4]]), (1, 0), 2),
    ],
)
def test_get(matrix: Matrix[bool], vector: Vector, result: int) -> None:
    assert matrix[vector] == result
