from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="отмена"),
]],
    resize_keyboard=True
)