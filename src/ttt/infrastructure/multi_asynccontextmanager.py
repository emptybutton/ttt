from asyncio import gather
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager


@asynccontextmanager
async def multi_asynccontextmanager[T](
    *managers: AbstractAsyncContextManager[T],
) -> AsyncIterator[list[T]]:
    result = await gather(*(manager.__aenter__() for manager in managers))  # noqa: PLC2801

    try:
        yield result
    except BaseException as error:  # noqa: BLE001
        await gather(*(
            manager.__aexit__(type(error), error, error.__traceback__)
            for manager in managers
        ))
    else:
        await gather(*(
            manager.__aexit__(None, None, None)
            for manager in managers
        ))
