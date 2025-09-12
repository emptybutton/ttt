from asyncio import sleep

from dishka import AsyncContainer

from ttt.application.invitation_to_game.game.auto_cancel_invitations_to_game import (  # noqa: E501
    AutoCancelInvitationsToGame,
)


async def auto_cancel_invitation_to_game_task(
    diska_container: AsyncContainer,
) -> None:
    while True:
        await sleep(1)
        async with diska_container() as request:
            cancel_invitations = await request.get(AutoCancelInvitationsToGame)
            await cancel_invitations()
