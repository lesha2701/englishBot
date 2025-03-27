from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

from utils.states import LessonStates
from utils.api import get_words_for_lessons

router = Router()


# Обработчик команды /new_lesson
@router.message(Command("new_lesson"))
async def start_new_lesson(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state in [LessonStates.PREVIEW, LessonStates.WORD_INTRODUCTION, LessonStates.TRANSLATION_PRACTICE]:
        await message.answer(
            "⚠️ У вас уже есть активный урок!\n"
            "Закончите его или используйте /cancel",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Отменить урок", callback_data="cancel_lesson")]
                ]
            )
        )
        return
        
    words = get_words_for_lessons(countWords=5)
    
    repetition = []
    for word in words:
        repetition.append({
            "word": word['english'],
            "translation": word['translation'],
            "rus_eng_count": 0,
            "eng_rus_count": 0,
            "total_count": 0
        })

    await state.update_data(
        words=words,
        current_word_index=0,
        count_words=5,
        repetition=repetition,
        current_word = {},
        mode = ""
    )
    await state.set_state(LessonStates.PREVIEW)
    
    words_preview = "\n".join(f"• <b>{word['english']}</b> - {word['translation']}" for word in words)
    
    await message.answer(
        f"🌿 <b>Урок №5!</b> 🌿\n"
        f"🌿 <b>Тема блока: Еда</b> 🌿\n\n"
        f"✨ <u>На этом уроке вы изучите {len(words)} новых слов</u> ✨\n\n"
        f"📖 <b>Список новых слов на этот урок:</b>\n"
        f"{words_preview}\n\n"
        f"🎯 <b>Структура урока:</b>\n"
        f"▫️ <i>Знакомство</i> — детальный разбор каждого слова\n"
        f"▫️ <i>Практика</i> — тренировка перевода\n"
        f"▫️ <i>Поддержка</i> — подсказки при затруднениях\n\n"
        f"⏳ <i>Среднее время: {len(words)} минуты</i>\n"
        f"💎 <i>Награда: {len(words)*10} монет</i>\n\n"
        f"<b>Совет:</b> Попробуйте мысленно составить предложения с этими словами перед началом!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Начать урок →", callback_data="start_lesson")],
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_lesson")]
            ]
        ),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "start_lesson", LessonStates.PREVIEW)
async def start_lesson(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await introduce_next_word(callback.message, state)

@router.callback_query(F.data == "cancel_lesson")
async def cancel_lesson_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Урок отменён")
    await callback.answer()

async def introduce_next_word(message: Message, state: FSMContext):
    data = await state.get_data()
    word = data["words"][data["current_word_index"]]
    example = random.choice(word["examples"])
    
    await message.answer(
        f"🎯 <b>Новое слово:</b>\n\n"
        f"<b>Английский:</b> {word['english']}\n"
        f"<b>Транскрипция:</b> [{word['transcription']}]\n"
        f"<b>Перевод:</b> {word['translation']}\n\n"
        f"<i>Пример:</i> {example['english']} - {example['translation']}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➡️ К практике", callback_data="to_practice")]
            ]
        )
    )
    await state.set_state(LessonStates.WORD_INTRODUCTION)

@router.callback_query(F.data == "to_practice", LessonStates.WORD_INTRODUCTION)
async def practice_translation_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await practice_translation(callback.message, state)


# # Функция тренировки перевода
async def practice_translation(message: Message, state: FSMContext):
    data = await state.get_data()
    word = data["words"][data["current_word_index"]]
    
    await message.answer(
        f"✏️ <b>Переведите на русский:</b>\n"
        f"<i>{word['english']}</i>"
    )
    await state.set_state(LessonStates.TRANSLATION_PRACTICE)

@router.message(LessonStates.TRANSLATION_PRACTICE)
async def check_translation(message: Message, state: FSMContext):
    data = await state.get_data()
    word = data["words"][data["current_word_index"]]
    user_answer = message.text.strip().lower()

    if user_answer == word['translation'].lower():
        await message.answer("✅ Верно! Отличная работа!")
        await state.update_data(current_word_index=data["current_word_index"] + 1)
        print(data["current_word_index"])

        if data["current_word_index"] >= (len(data["words"]) - 1):
            await message.answer(
                f"🎉 <b>Отлично! Мы познакомились со всеми новыми словами!</b>\n\n"
                f"✨ <i>Теперь закрепим результат через «Умное повторение»</i> ✨\n\n"
                f"🔁 <b>Как это работает:</b>\n"
                f"▫️ Случайный порядок слов, каждое слово надо будет написать:\n"
                f"▫️ 2 раза с русского на английский\n"
                f"▫️ 1 раз с английского на русский\n\n"
                f"🧠 <i>Такой подход поможет лучше запомнить слова</i>\n\n"
                f"<b>Совет:</b> Попробуйте сначала вспомнить слово мысленно, прежде чем писать ответ!\n\n"
                f"⏳ <i>Примерное время: {len(data['words'])*1.5} минут</i>\n\n"
                f"<b>Готовы начать повторение?</b>",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🔁 Начать повторение", callback_data="start_repetition")]
                    ]
                ),
                parse_mode="HTML"
            )
            await state.set_state(LessonStates.REPETITION)
        else:
            await state.set_state(LessonStates.WORD_INTRODUCTION)
            await introduce_next_word(message, state)

    else:
        hint = random.choice([
                f"Первая буква: <b>{word['translation'][0].upper()}</b>",
                f"Количество букв: {len(word['translation'])}",
                f"Пример: {random.choice(word['examples'])}",
                f"Синоним: {random.choice(word.get('synonyms', ['нет синонимов']))}",
                f"Транскрипция: {word['transcription']}"
            ])
        await message.answer(f"❌ Почти! Подсказка: {hint}")

@router.callback_query(F.data == "start_repetition", LessonStates.REPETITION)
async def repetition_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await repetition_translation(callback.message, state)

async def repetition_translation(message: Message, state: FSMContext):
    data = await state.get_data()
    repetition = data["repetition"]
    print(repetition)

    available_words = [
        word for word in repetition 
        if word['rus_eng_count'] < 2 or word['eng_rus_count'] < 1
    ]

    if not available_words:
        await finish_lesson(message, state)
        return

    randomWord = random.choice(available_words)
    while randomWord == data["current_word"]:
        randomWord = random.choice(available_words)
    await state.update_data(current_word=randomWord)

    modes = []
    if randomWord['rus_eng_count'] < 2:
        modes.append('rus_eng')
    if randomWord['eng_rus_count'] < 1:
        modes.append('eng_rus')

    selected_mode = random.choice(modes)

    if selected_mode == 'rus_eng':
        question = f"🔤 <b>Переведите на английский:</b>\n<code>{randomWord['translation']}</code>"
        await state.update_data(mode='rus_eng')
    else:
        question = f"🔤 <b>Переведите на русский:</b>\n<code>{randomWord['word']}</code>"
        await state.update_data(mode='eng_rus')
    
    await message.answer(question)
    await state.set_state(LessonStates.CHECK_REPETITION)

@router.message(LessonStates.CHECK_REPETITION)
async def check_repetition(message: Message, state: FSMContext):
    # Получаем текущие данные из состояния
    data = await state.get_data()
    current_word = data["current_word"]
    user_answer = message.text.strip().lower()
    
    # Создаем копию списка repetition для изменения
    repetition = data["repetition"].copy()
    
    # Находим индекс текущего слова в списке repetition
    word_index = next((i for i, w in enumerate(repetition) 
                      if w["word"] == current_word["word"]), None)
    
    if word_index is None:
        await message.answer("⚠️ Ошибка: слово не найдено в списке повторения")
        return
    
    # Проверяем ответ и обновляем счетчики
    if user_answer == current_word['translation'].lower() or user_answer == current_word['word'].lower():
        await message.answer("✅ Верно! Отличная работа!")
        
        if data["mode"] == 'rus_eng':
            repetition[word_index]['rus_eng_count'] += 1
        else:
            repetition[word_index]['eng_rus_count'] += 1

        repetition[word_index]['total_count'] += 1
        # Обновляем данные в состоянии
        await state.update_data(
            repetition=repetition,
            current_word=repetition[word_index]
        )

        await state.set_state(LessonStates.REPETITION)
        await repetition_translation(message, state)

    else:
        hint = random.choice([
                f"Первая буква: <b>{current_word['translation'][0].upper()}</b>",
                f"Количество букв: {len(current_word['translation'])}",
                f"Пример: {random.choice(current_word['examples'])}",
                f"Синоним: {random.choice(current_word.get('synonyms', ['нет синонимов']))}",
                f"Транскрипция: {current_word['transcription']}"
            ])
        await message.answer(f"❌ Почти! Подсказка: {hint}")


async def finish_lesson(message: Message, state: FSMContext):
    data = await state.get_data()
    
    await message.answer(
        f"🎉 <b>Урок завершен!</b>\n\n"
        f"🔹 Изучено слов: {len(data['words'])}\n"
        f"💰 Получено монет: {len(data['words']) * 10}\n\n"
        f"Повторите эти слова через /repeat\n"
        f"Новый урок будет доступен завтра!"
    )
    await state.clear()


# # Обработчик ответов пользователя
# @router.message(LessonStates.TRANSLATION_PRACTICE)
# async def check_translation(message: Message, state: FSMContext):
#     data = await state.get_data()
#     word_id = data["words"][data["current_word_index"]]
#     word = get_word_details(word_id)
#     user_answer = message.text.strip().lower()
    
#     if user_answer == word['translation'].lower():
#         # Правильный ответ
#         await message.answer("✅ Верно! Отличная работа!")
        
#         # Обновляем прогресс
#         update_word_progress(word_id, is_correct=True)
        
#         # Переходим к следующему слову
#         await state.update_data(current_word_index=data["current_word_index"] + 1)
#         data = await state.get_data()
        
#         if data["current_word_index"] >= len(data["words"]):
#             # Урок завершен
#             await finish_lesson(message, state)
#         else:
#             await introduce_next_word(message, state)
#     else:
#         # Неправильный ответ
#         attempts = update_word_progress(word_id, is_correct=False)
        
#         if attempts == 1:
#             # Первая подсказка
#             hint = random.choice([
#                 f"Первая буква: <b>{word['translation'][0].upper()}</b>",
#                 f"Количество букв: {len(word['translation'])}"
#             ])
#             await message.answer(f"❌ Почти! Подсказка: {hint}")
#         elif attempts >= 2:
#             # Вторая подсказка
#             hint = random.choice([
#                 f"Пример: {random.choice(word['examples'])}",
#                 f"Синоним: {random.choice(word.get('synonyms', ['нет синонимов']))}"
#             ])
#             await message.answer(f"💡 Еще подсказка: {hint}")

# # Завершение урока