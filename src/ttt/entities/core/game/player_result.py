from ttt.entities.core.game.ai import AiDraw, AiLoss, AiWin
from ttt.entities.core.user.draw import UserDraw
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.win import UserWin


type PlayerLoss = UserLoss | AiLoss
type PlayerDraw = UserDraw | AiDraw
type PlayerWin = UserWin | AiWin

type PlayerResult = PlayerWin | PlayerLoss | PlayerDraw
