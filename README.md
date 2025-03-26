English Learning Telegram Bot
📌 О проекте
Telegram-бот для изучения английского языка с интерактивными упражнениями, словарными тренировками и грамматическими тестами. Бот помогает пользователям систематически улучшать свой английский через игровые механики и персонализированный подход.

✨ Основные функции
📚 Изучение новых слов
    Структурированные уроки с настраиваемым количеством слов (10 по умолчанию)
    Адаптивный подбор слов по:
     - Уровню пользователя (новичок, средний, продвинутый)
     - Тематике (еда, путешествия, бизнес и др.)
     - Частотности использования

    Формат обучения:
     - Показ английского слова + транскрипция
     - Пользователь вводит перевод
     - Необходимо правильно ввести слово 3 раза
     - Подсказки после ошибок

    Ограничение: 1 бесплатный урок в день для пользователей без подписки

🔁 Повторение изученных слов
    Случайные уведомления с изученными словами
    Пользователь получает слово на английском и вводит перевод
    Для подписчиков - настройка количества повторений в день

🔔 Система напоминаний
    Уведомления о:
     - Доступном бесплатном уроке
     - Необходимости повторить слова
     - Тематические напоминания (для подписчиков)

🎮 Игровые механики
    Внутриигровая валюта за:
     - Прохождение уроков
     - Выполнение ежедневных заданий
     - Активность (стрики)
    
    Магазин для покупки:
     - Дополнительных уроков
     - Временной подписки

    Розыгрыши Telegram Premium для активных пользователей

📖 Теоретические материалы
     - Готовые статьи по грамматике
     - Справочник с примерами использования

✏️ Генерация тестов
    - Персонализированные тесты по шаблонам. Доступно только для подписчиков

🛠 Техническая реализация
🔧 Технологии
    Язык программирования: Python (aiogram / python-telegram-bot)

    База данных: MySQL

    Хостинг: -

🗃 Структура базы данных
Основные таблицы:
     - Пользователи (users) - данные пользователей, настройки, прогресс
     - Подписки (subscriptions) - информация о статусе подписки
     - Достижения (achievements) - полученные достижения
     - Изученные слова (learned_words) - словарь пользователя
     - Статистика (user_stats) - прогресс обучения

🤖 Команды бота

    Основные:
    /start	Начало работы, выбор уровня
    /help	Справка по командам
    /profile	Статистика и прогресс
    /settings	Настройки уведомлений

    Обучение
    /new_lesson	Начать новый урок
    /topics	Выбрать тематику слов
    /repeat	Повторить изученные слова
    /grammar	Теоретические материалы

    Игровые
    /shop	Магазин улучшений
    /tasks	Ежедневные задания
    /streak	Текущая серия дней
    /leaderboard	Топ пользователей

    Администрирование
    /add_admin	Назначить администратора
    /send_all	Рассылка сообщений
    /block	Блокировка пользователя
