from contextlib import AbstractAsyncContextManager
from typing import Any


Transaction = AbstractAsyncContextManager[Any]
