from typing import Any

from dishka.integrations.taskiq import CONTAINER_NAME
from taskiq import TaskiqMessage, TaskiqMiddleware, TaskiqResult

from ttt.infrastructure.dishka.next_container import NextContainer


class TaskiqNextContainerMiddleware(TaskiqMiddleware):
    def __init__(self, next_container: NextContainer) -> None:
        super().__init__()
        self._next_container = next_container

    async def pre_execute(
        self,
        message: TaskiqMessage,
    ) -> TaskiqMessage:
        next_container = self._next_container({TaskiqMessage: message})

        container = await next_container.__aenter__()  # noqa: PLC2801
        message.labels[CONTAINER_NAME] = container
        return message

    async def on_error(
        self,
        message: TaskiqMessage,  # noqa: ARG002
        result: TaskiqResult[Any],
        exception: BaseException,  # noqa: ARG002
    ) -> None:
        if CONTAINER_NAME in result.labels:
            await result.labels[CONTAINER_NAME].close()
            del result.labels[CONTAINER_NAME]

    async def post_execute(
        self,
        message: TaskiqMessage,  # noqa: ARG002
        result: TaskiqResult[Any],
    ) -> None:
        if CONTAINER_NAME in result.labels:
            await result.labels[CONTAINER_NAME].close()
            del result.labels[CONTAINER_NAME]
