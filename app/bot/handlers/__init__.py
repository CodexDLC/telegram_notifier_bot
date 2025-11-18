# init routers
from aiogram import Router

from .commands import router as command_router


bot_router = Router()


bot_router.include_routers(
    command_router

)