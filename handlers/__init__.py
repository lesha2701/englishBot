from aiogram import Router


def setup_message_routers() -> Router:
    from . import start, lesson

    router = Router()
    router.include_router(start.router)
    router.include_router(lesson.router)
    return router