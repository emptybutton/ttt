from typing import Any, Literal, NoReturn, overload


def not_none[ValueT](
    value: ValueT | None,
    else_: Exception | type[Exception] = ValueError,
) -> ValueT:
    if value is not None:
        return value

    raise else_


def none(
    value: Any,  # noqa: ANN401
    else_: Exception | type[Exception] = ValueError,
) -> None:
    if value is not None:
        raise else_


@overload
def assert_(
    assertion: Literal[False],
    else_: Exception | type[Exception] = ValueError,
) -> NoReturn: ...


@overload
def assert_(
    assertion: Literal[True],
    else_: Exception | type[Exception] = ValueError,
) -> None: ...


@overload
def assert_(
    assertion: Any,  # noqa: ANN401
    else_: Exception | type[Exception] = ValueError,
) -> None: ...


def assert_(
    assertion: Any,
    else_: Exception | type[Exception] = ValueError,
) -> None:
    if not assertion:
        raise else_
