from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Hello, AIOgram 3.x!")