from collections.abc import Iterator
from contextlib import contextmanager

from psycopg.errors import SerializationFailure
from sqlalchemy.exc import OperationalError

from ttt.application.common.errors.serialization_error import SerializationError


@contextmanager
def reraise_serialization_error() -> Iterator[None]:
    try:
        yield
    except OperationalError as error:
        if isinstance(error.orig, SerializationFailure):
            raise SerializationError from error

        raise error from error
