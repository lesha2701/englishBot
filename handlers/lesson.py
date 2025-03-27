from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

from utils.states import LessonStates
from utils.api import get_words_for_lessons

from typing import Dict, List

router = Router()

WordDict = Dict[str, str | int | List[Dict[str, str]]]

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
    
    repetition = [{
        "word": word['english'],
        "translation": word['translation'],
        "transcription": word.get('transcription', ''),
        "examples": word.get('examples', []),
        "synonyms": word.get('synonyms', []),
        "rus_eng_count": 0,
        "eng_rus_count": 0,
        "total_count": 0
    } for word in words]

    await state.update_data(
        words=words,
        current_word_index=0,
        count_words=5,
        repetition=repetition,
        current_word = {},
        mode = "",
        errors=0
    )
    await state.set_state(LessonStates.PREVIEW)
    
    words_preview = "\n".join(f"• <b>{word['english']}</b> - {word['translation']}" for word in words)
    
    await message.answer(
        f"🌿 <b>Урок №5! Тема: Еда</b> 🌿\n\n"
        f"✨ Изучите {len(words)} новых слов:\n"
        f"{words_preview}\n\n"
        f"🎯 Формат урока:\n"
        f"▫️ Знакомство с каждым словом\n"
        f"▫️ Практика перевода\n"
        f"▫️ Подсказки при затруднениях\n\n"
        f"⏱ Время: ~{len(words)} мин | 🏆 Награда: {len(words)*10} монет\n\n"
        f"<i>Совет: Попробуйте составить предложения с этими словами!</i>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Начать", callback_data="start_lesson")],
                [InlineKeyboardButton(text="⏸ Позже", callback_data="cancel_lesson")]
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
                f"⏱ ~{len(data['words'])*1.5} мин\n\n"
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
        countErrors = data["errors"] + 1
        await state.update_data(errors=countErrors)
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
    
    is_correct = (data["mode"] == 'rus_eng' and user_answer == current_word['word'].lower()) or \
                 (data["mode"] == 'eng_rus' and user_answer == current_word['translation'].lower())

    # Проверяем ответ и обновляем счетчики
    if is_correct:
        await message.answer("✅ <b>Верно!</b> Так держать!", parse_mode="HTML")
        
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
        hint = await generate_hint(current_word, is_english_to_russian=data["mode"] == 'eng_rus')
        countErrors = data["errors"] + 1
        await state.update_data(errors=countErrors)
        await message.answer(f"❌ Неверно. {hint}", parse_mode="HTML")

async def generate_hint(word: WordDict, is_english_to_russian: bool) -> str:
    """Генерация подсказки в зависимости от направления перевода"""
    hints = []
    
    if is_english_to_russian:
        hints.extend([
            f"Первая буква: <b>{word['translation'][0].upper()}</b>",
            f"Количество букв: {len(word['translation'])}"
        ])
    else:
        hints.extend([
            f"Транскрипция: <b>{word.get('transcription', '')}</b>",
            f"Начинается на: <b>{word['word'][0].upper()}</b>"
        ])
    
    if word.get('examples'):
        example = random.choice(word['examples'])
        hints.append(f"Пример: {example['english']} - {example['translation']}")
    
    if word.get('synonyms'):
        hints.append(f"Синоним: {random.choice(word['synonyms'])}")
    
    return random.choice(hints)


async def finish_lesson(message: Message, state: FSMContext):
    """Завершение урока с статистикой"""
    data = await state.get_data()
    total_words = len(data["words"])
    correct_answers = sum(w['total_count'] for w in data["repetition"])
    errors = data["errors"]
    reward = total_words * 10 + correct_answers * 2
    
    await message.answer(
        f"🏁 <b>Урок завершен!</b>\n\n"
        f"📊 Результаты:\n"
        f"• Изучено слов: {total_words}\n"
        f"• Правильных ответов: {correct_answers}\n"
        f"• Неправильных ответов: {errors}\n"
        f"💰 Награда: {reward} монет\n\n"
        f"<i>Следующий урок будет доступен завтра</i>",
        parse_mode="HTML"
    )
    await state.clear()
