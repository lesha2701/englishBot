from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    english_level = State()

class LessonStates(StatesGroup):
    PREVIEW = State()
    WORD_INTRODUCTION = State()
    TRANSLATION_PRACTICE = State()
    REPETITION = State()
    CHECK_REPETITION = State()