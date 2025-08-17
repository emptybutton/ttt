from dataclasses import asdict, dataclass
from typing import Any, Literal

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import (
    Button,
    Group,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Multi, Text
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F, MagicFilter

from ttt.application.game.game.cancel_game import CancelGame
from ttt.application.game.game.make_move_in_game import MakeMoveInGame
from ttt.application.game.game.start_game_with_ai import StartGameWithAi
from ttt.application.game.game.view_game import ViewGame
from ttt.application.game.game.wait_game import WaitGame
from ttt.application.user.emoji_selection.select_emoji import SelectEmoji
from ttt.application.user.stars_purchase.start_stars_purchase import (
    StartStarsPurchase,
)
from ttt.application.user.view_main_menu import ViewMainMenu
from ttt.application.user.view_user import ViewUser
from ttt.application.user.view_user_emojis import ViewUserEmojis
from ttt.entities.core.game.ai import AiType
from ttt.entities.core.game.cell_number import CellNumber
from ttt.entities.core.game.game import Game
from ttt.entities.core.game.game_result import (
    CancelledGameResult,
    DecidedGameResult,
    DrawGameResult,
)
from ttt.entities.core.user.draw import UserDraw
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.win import UserWin
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.texts import (
    copy_signed_text,
    short_float_text,
)
from ttt.presentation.result_buffer import ResultBuffer


class DialogState(StatesGroup):
    main = State()
    emojis = State()
    profile = State()
    game_mode_to_start_game = State()
    ai_type_to_start_game = State()
    active_game = State()
    completed_game = State()
    shop = State()
    emoji_shop = State()
    stars_shop = State()


class Hint(Text):
    def __init__(self, text: Text, hint_key: str = "hint") -> None:
        super().__init__(when=F["start_data"][hint_key])

        self.text = text
        self.hint_key = hint_key

    async def _render_text(
            self, data: dict[str, Any], manager: DialogManager,
    ) -> str:
        text = await self.text.render_text(data, manager)

        if isinstance(manager.start_data, dict):
            del manager.start_data[self.hint_key]

        return text


@dataclass(frozen=True)
class EncodableToWindowData:
    def window_data(self) -> dict[str, Any]:
        return {self._data_key(): asdict(self)}

    def _data_key(self) -> str:
        return "main"


@dataclass(frozen=True)
class MainMenuView(EncodableToWindowData):
    is_user_in_game: bool
    has_user_emojis: bool

    def _data_key(self) -> str:
        return "common"


@inject
async def main_getter(
    *,
    event_from_user: User,
    view_main_menu: FromDishka[ViewMainMenu],
    result_buffer: FromDishka[ResultBuffer],
    dialog_manager: DialogManager,
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    completed_game_view_exists = (
        isinstance(dialog_manager.start_data, dict)
        and "completed_game" in dialog_manager.start_data
    )

    if completed_game_view_exists:
        return {}

    await view_main_menu(event_from_user.id)
    view = result_buffer(MainMenuView)

    return view.window_data()


@inject
async def on_cancel_game_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    cancel_game: FromDishka[CancelGame],
) -> None:
    await cancel_game(callback.from_user.id)


@dataclass(frozen=True)
class CompletedGameView(EncodableToWindowData):
    type_: Literal["win", "loss", "draw", "cancelled_game"]
    rating_vector_text: str | None
    new_stars: int | None
    has_user_emojis: bool

    def _data_key(self) -> str:
        return "completed_game"

    @classmethod
    def of(cls, game: Game, user_id: int) -> "CompletedGameView":
        match game.result:
            case DecidedGameResult(
                win=UserWin(user_id=winner_id) as win,
            ) if winner_id == user_id:
                type_ = "win"
                rating_vector = win.rating_vector
                new_stars = win.new_stars

            case DecidedGameResult(
                loss=UserLoss(user_id=loser_id) as loss,
            ) if loser_id == user_id:
                type_ = "loss"
                rating_vector = loss.rating_vector
                new_stars = None

            case DrawGameResult(draw1, draw2):
                if isinstance(draw1, UserDraw) and draw1.user_id == user_id:
                    draw = draw1
                elif isinstance(draw2, UserDraw) and draw2.user_id == user_id:
                    draw = draw2
                else:
                    raise ValueError

                type_ = "draw"
                rating_vector = draw.rating_vector
                new_stars = None

            case CancelledGameResult():
                type_ = "cancelled_game"
                rating_vector = None
                new_stars = None

            case _:
                raise ValueError

        if rating_vector is None:
            rating_vector_text = None
        else:
            rating_vector_text = copy_signed_text(
                short_float_text(rating_vector), rating_vector,
            )

        user = not_none(game.user(user_id))

        return CompletedGameView(
            type_=type_,
            rating_vector_text=rating_vector_text,
            new_stars=new_stars,
            has_user_emojis=bool(user.emojis),
        )


@inject
async def on_back_to_game_clicked(
    callback: CallbackQuery,
    _: Button,
    manager: DialogManager,
    view_game: FromDishka[ViewGame],
    result_buffer: FromDishka[ResultBuffer],
) -> None:
    await view_game(callback.from_user.id)
    view = result_buffer(ActiveGameView)
    data = view.window_data()

    await manager.start(DialogState.active_game, data, StartMode.RESET_STACK)


completed_game_f = F["start_data"]["completed_game"]

rating_f = completed_game_f["rating_vector_text"].is_not(None)
stars_f = completed_game_f["new_stars"].is_not(None)
has_user_emojis_f = (
    F["common"]["has_user_emojis"] | completed_game_f["has_user_emojis"]
)
is_user_not_in_game_f = completed_game_f | ~F["common"]["is_user_in_game"]


main_window = Window(
    Const("🧭 Меню", when=~completed_game_f & ~F["start_data"]["hint"]),

    Hint(
        Multi(
            Case(
                selector=completed_game_f["type_"],
                texts={
                    "win": Const("🎆 Вы победили!"),
                    "loss": Const("💀 Вы проиграли!"),
                    "draw": Const("🕊 Ничья!"),
                    "cancelled_game": Const("👻 Игра отменена!"),
                },
                when=completed_game_f,
            ),
            Const(" ", when=(rating_f | stars_f)),
            Format(
                "{start_data[completed_game][rating_vector_text]} 🏅",
                when=rating_f,
            ),
            Format("+{start_data[completed_game][new_stars]} 🌟", when=stars_f),
        ),
        hint_key="completed_game",
    ),

    Hint(Format("{start_data[hint]}")),

    SwitchTo(
        Const("Начать игру"),
        id="start_game",
        state=DialogState.game_mode_to_start_game,
        when=is_user_not_in_game_f,
    ),
    Button(
        Const("Продолжить игру"),
        id="back_to_game",
        on_click=on_back_to_game_clicked,
        when=~is_user_not_in_game_f,
    ),
    Button(
        Const("Отменить игру"),
        id="cancel_game",
        when=~is_user_not_in_game_f,
        on_click=on_cancel_game_clicked,
    ),
    SwitchTo(
        Const("Профиль"),
        id="profile",
        state=DialogState.profile,
    ),
    SwitchTo(
        Const("Эмоджи"),
        id="emojis",
        state=DialogState.emojis,
        when=has_user_emojis_f,
    ),
    SwitchTo(
        Const("Магазин"),
        id="shop",
        state=DialogState.shop,
    ),
    state=DialogState.main,
    getter=main_getter,
)


@inject
async def on_game_against_user_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    wait_game: FromDishka[WaitGame],
) -> None:
    await wait_game(callback.from_user.id)


game_start_window = Window(
    Const("⚔️ Выберите режим игры", when=~F["start_data"]["hint"]),
    Hint(Format("{start_data[hint]}")),
    Row(
        Button(
            Const("👥 Против человека"),
            id="game_against_user",
            on_click=on_game_against_user_clicked,
        ),
        SwitchTo(
            Const("🤖 Против ИИ"),
            id="game_against_ai",
            state=DialogState.ai_type_to_start_game,
        ),
    ),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.game_mode_to_start_game,
)


@inject
async def on_game_against_gemini_2_0_flash_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    start_game_with_ai: FromDishka[StartGameWithAi],
) -> None:
    await start_game_with_ai(callback.from_user.id, AiType.gemini_2_0_flash)


ai_type_to_start_game_window = Window(
    Const("🤖 Выберите тип ИИ"),
    Row(
        Button(
            Const("gemini 2.0 flash"),
            id="game_against_gemini_2_0_flash",
            on_click=on_game_against_gemini_2_0_flash_clicked,
        ),
    ),
    SwitchTo(
        Const("Назад"), id="back", state=DialogState.game_mode_to_start_game,
    ),
    state=DialogState.ai_type_to_start_game,
)


@inject
async def on_cell_clicked(
    callback: CallbackQuery,
    button: Button,
    _: DialogManager,
    make_move_in_game: FromDishka[MakeMoveInGame],
) -> None:
    cell_number_int = int(not_none(button.widget_id)[-1])
    await make_move_in_game(callback.from_user.id, cell_number_int)


def cell_button(cell_number_int: int) -> Button:
    return Button(
        Format(
            f"{{start_data[main][cell_view_by_cell_number_int][_{cell_number_int}]}}",
        ),
        id=f"game_cell_{cell_number_int}",
        on_click=on_cell_clicked,
    )


@dataclass(frozen=True)
class ActiveGameView(EncodableToWindowData):
    is_current_players_move_expected: bool
    cell_view_by_cell_number_int: dict[str, str]
    is_user_player1: bool
    player1_emoji: str
    player2_emoji: str

    @classmethod
    def of(cls, game: Game, user_id: int) -> "ActiveGameView":
        cell_view_by_cell_number_int = dict[str, str]()

        for cell_number_int in range(1, 10):
            cell_number = CellNumber(cell_number_int)
            cell_emoji_ = game.cell_emoji(cell_number.board_position())

            cell_view = " " if cell_emoji_ is None else cell_emoji_.str_
            cell_view_by_cell_number_int[f"_{cell_number_int}"] = cell_view

        return ActiveGameView(
            is_current_players_move_expected=game.is_player_move_expected(
                user_id,
            ),
            cell_view_by_cell_number_int=cell_view_by_cell_number_int,
            is_user_player1=game.player1.id == user_id,
            player1_emoji=game.player1_emoji.str_,
            player2_emoji=game.player2_emoji.str_,
        )


active_game_window = Window(
    Case(selector=F["start_data"]["main"]["is_user_player1"], texts={
        True: Format(
            "Вы — {start_data[main][player1_emoji]}"
            ", Враг — {start_data[main][player2_emoji]}",
        ),
        False: Format(
            "Враг — {start_data[main][player1_emoji]}"
            ", Вы — {start_data[main][player2_emoji]}",
        ),
    }),
    Case(
        selector=F["start_data"]["main"]["is_current_players_move_expected"],
        texts={
            True: Const("Ходите"),
            False: Const("Ждите хода врага"),
        },
    ),
    Hint(Multi(Const(" "), Format("{start_data[hint]}"))),
    Group(
        Row(cell_button(1), cell_button(2), cell_button(3)),
        Row(cell_button(4), cell_button(5), cell_button(6)),
        Row(cell_button(7), cell_button(8), cell_button(9)),
    ),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.active_game,
)


@dataclass(frozen=True)
class EmojiView:
    emoji_str: str
    is_emoji_selected: bool

    def __str__(self) -> str:
        return (
            f"<{self.emoji_str}>" if self.is_emoji_selected else self.emoji_str
        )


@dataclass(frozen=True)
class EmojiMenuView(EncodableToWindowData):
    emoji_views: tuple[EmojiView, ...]
    is_any_emoji_selected: bool

    def need_to_paginate(self) -> bool:
        return len(self.emoji_views) > 7  # noqa: PLR2004


@inject
async def emoji_getter(
    *,
    event_from_user: User,
    view_user_emojis: FromDishka[ViewUserEmojis],
    result_buffer: FromDishka[ResultBuffer],
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    await view_user_emojis(event_from_user.id)
    view = result_buffer(EmojiMenuView)

    return view.window_data()


@inject
async def on_emoji_selected(
    callback: CallbackQuery,
    _: Widget,
    __: DialogManager,
    emoji_str: str,
    select_emoji: FromDishka[SelectEmoji],
) -> None:
    await select_emoji(callback.from_user.id, emoji_str)


emoji_window = Window(
    Const("🎭 Эмоджи"),
    Select(
        Format("{item}"),
        id="not_paginated_emojis",
        item_id_getter=lambda it: it.emoji_str,
        items=F["main"]["emoji_views"],
        on_click=on_emoji_selected,
        when=~F["main"]["need_to_paginate"],
    ),
    ScrollingGroup(
        Select(
            Format("{item}"),
            id="paginated_emojis_page",
            item_id_getter=lambda it: it.emoji_str,
            items=F["main"]["emoji_views"],
            on_click=on_emoji_selected,
        ),
        width=4,
        height=4,
        id="paginated_emojis",
        when=F["main"]["need_to_paginate"],
    ),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.emojis,
    getter=emoji_getter,
)


@dataclass(frozen=True)
class UserProfileView(EncodableToWindowData):
    number_of_wins: int
    number_of_draws: int
    number_of_defeats: int
    account_stars: int
    rating_text: str

    @classmethod
    def of(
        cls,
        number_of_wins: int,
        number_of_draws: int,
        number_of_defeats: int,
        account_stars: int,
        rating: float,
    ) -> "UserProfileView":
        return UserProfileView(
            number_of_wins=number_of_wins,
            number_of_draws=number_of_draws,
            number_of_defeats=number_of_defeats,
            account_stars=account_stars,
            rating_text=short_float_text(rating),
        )


@inject
async def profile_getter(
    *,
    event_from_user: User,
    view_user: FromDishka[ViewUser],
    result_buffer: FromDishka[ResultBuffer],
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    await view_user(event_from_user.id)
    view = result_buffer(UserProfileView)

    return view.window_data()


profile_window = Window(
    Multi(
        Const("🎭 Профиль"),
        Const(" "),
        Format("🌟 Звёзд: {main[account_stars]}"),
        Format("🏅 Рейтинг: {main[rating_text]}"),
        Format("🏆 Побед: {main[number_of_wins]}"),
        Format("💀 Поражений: {main[number_of_defeats]}"),
        Format("🕊️ Ничьих: {main[number_of_draws]}"),
    ),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.profile,
    getter=profile_getter,
)


shop_window = Window(
    Const("🛒 Что хотите купить?"),
    Row(
        SwitchTo(
            Const("🌟 Звёзды"),
            id="stars_shop",
            state=DialogState.stars_shop,
        ),
        SwitchTo(
            Const("🎭 Эмоджи"),
            id="emoji_shop",
            state=DialogState.emoji_shop,
        ),
    ),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.shop,
    getter=profile_getter,
)


@inject
async def on_stars_purchase_clicked(
    callback: CallbackQuery,
    button: Button,
    _: DialogManager,
    start_stars_purchase: FromDishka[StartStarsPurchase],
) -> None:
    match button.widget_id:
        case "8192_stars_purchase":
            stars = 8192
        case "16384_stars_purchase":
            stars = 16384
        case "32768_stars_purchase":
            stars = 32768
        case "65536_stars_purchase":
            stars = 65536
        case _:
            raise ValueError(button.widget_id)

    await start_stars_purchase(callback.from_user.id, stars)


@inject
async def stars_shop_getter(  # noqa: RUF029
    *,
    dialog_manager: DialogManager,
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    return {
        "has_start_hint": (
            isinstance(dialog_manager.start_data, dict)
            and "hint" in dialog_manager.start_data
        ),
    }


stars_shop_window = Window(
    Const("🌟 Сколько звёзд хотите купить?", when=~F["start_data"]["hint"]),
    Row(
        Button(
            Const("8192 🌟 (128₽)"),
            id="8192_stars_purchase",
            on_click=on_stars_purchase_clicked,
        ),
        Button(
            Const("16384 🌟 (256₽)"),
            id="16384_stars_purchase",
            on_click=on_stars_purchase_clicked,
        ),
        when=~F["has_start_hint"],
    ),
    Row(
        Button(
            Const("32768 🌟 (512₽)"),
            id="32768_stars_purchase",
            on_click=on_stars_purchase_clicked,
        ),
        Button(
            Const("65536 🌟 (1024₽)"),
            id="65536_stars_purchase",
            on_click=on_stars_purchase_clicked,
        ),
        when=~F["has_start_hint"],
    ),

    Hint(Format("{start_data[hint]}")),

    SwitchTo(Const("Назад"), id="back", state=DialogState.shop),
    state=DialogState.stars_shop,
    getter=stars_shop_getter,
)


dialog = Dialog(
    main_window,
    game_start_window,
    ai_type_to_start_game_window,
    active_game_window,
    profile_window,
    emoji_window,
    shop_window,
    stars_shop_window,
)
