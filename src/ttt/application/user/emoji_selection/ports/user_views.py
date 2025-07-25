from abc import ABC, abstractmethod


class EmojiSelectionUserViews(ABC):
    @abstractmethod
    async def invalid_emoji_to_select_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_not_purchased_to_select_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_selected_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def wait_emoji_to_select_view(
        self,
        user_id: int,
        /,
    ) -> None: ...
