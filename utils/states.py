from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    english_level = State()