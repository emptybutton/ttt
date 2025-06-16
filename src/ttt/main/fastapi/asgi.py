from ttt.main.common.asgi import LazyASGIApp
from ttt.main.fastapi.di import container
from ttt.presentation.fastapi.app import app_from


app = LazyASGIApp(app_factory=lambda: app_from(container))
