from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

worker_no_job = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Проверить наличие обновлений"),
        ],
    ],
    resize_keyboard=True
)

