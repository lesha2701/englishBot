from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

from keyboards.builders import englishLevel
from utils.states import Registration

import json

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Registration.english_level)
    await message.answer('''
✨ <b>Привет, будущий полиглот!</b> ✨

Я твой личный тренер по английскому — <b>EnglishBoostBot</b>! 
С моей помощью ты сможешь:

🚀 <b>Прокачать словарный запас</b> по умной системе
🧠 <b>Запоминать надолго</b> с интервальными повторениями
🎮 <b>Учиться играючи</b> — с ачивками и бонусами
📈 <b>Видеть прогресс</b> в реальном времени

<b>Давай знакомиться ближе!</b>  

👇 <i>Для старта выбери свой уровень английского:</i>
    ''',
    reply_markup=englishLevel(["Начинающий", "Средний", "Продвинутый"])
    )


@router.message(Registration.english_level, F.text.in_(["Начинающий", "Средний", "Высокий"]))
async def form_english_level(message: Message, state: FSMContext) -> None:
    if message.text == "Начинающий":
        await state.update_data(level=1)
    elif message.text == "Средний":
        await state.update_data(level=2)
    elif message.text == "Высокий":
        await state.update_data(level=3)

    data = await state.get_data()
    registerUser = {
        "telegram_id": message.from_user.id,
        "level": data["level"],
        "coins": 50
    }
    registerUser_json = json.dumps(registerUser, ensure_ascii=False, indent=2)
    print(registerUser_json)

    await message.answer('''
🎊 <b>Добро пожаловать в семью EnglishBoostBot!</b> 🎊

<b>Твой путь к свободному английскому начинается здесь и сейчас!</b> 🌟

📝 <b>Основы нашего успеха:</b>
✅ <b>1 урок в день</b> - минимум, который меняет всё (безлимит с /premium)
✅ <b>+50 стартовых монет</b> (открывают мир возможностей в /shop)
✅ <b>Право на ошибку</b> - после 2х попыток я помогу 💡
✅ <b>Система повторений /repeat</b> - твой ключ к идеальной памяти 🔑

💰 <b>Твой стартовый набор:</b>
┏ 50 бонусных монет 
┃ (вот твой первый капитал!)
┗ Доступ к:
   • Ускоренным урокам 🚀
   • Тематическим коллекциям 🗃️
   • Спецтренировкам 🏋️

💫 <b>"Каждый эксперт когда-то был новичком, который не сдался!"</b> 💫

📌 <b>Простой старт:</b>
Просто нажми /new_lesson - и пусть твое путешествие начнется!

💡 <b>Всегда под рукой:</b>
Команда /help - твой персональный гид по всем возможностям:
   • Полный список команд 📋
   • Примеры использования 💬
   • Лайфхаки для учебы 🧠

<b>P.S.</b> Мечтаешь о прорыве? 
/premium откроет безграничные горизонты! 🔥

🌍 <b>"Язык - это не барьер, а мост к новым мирам. Пора его построить!"</b> 🌍
''')

    