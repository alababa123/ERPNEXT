from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

reg = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Зарегистрироваться"),
        ],
    ],
    resize_keyboard=True
)

