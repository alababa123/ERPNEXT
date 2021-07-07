from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

foreman_start_job = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Начать рабочий день"),
        ],
    ],
    resize_keyboard=True
)

