from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.foreman_menu_callback import f_m
worker_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Сделать отчет", callback_data=f_m.new(name="Сделать отчет")
            )
        ],
        [
          InlineKeyboardButton(text="Перевести в термины компании", callback_data=f_m.new(name="Перевести в термины компании"))
        ],
        [
            InlineKeyboardButton(text="Закончить рабочий день", callback_data=f_m.new(name="Закончить рабочий день")
            )
        ]
    ]
)
worker_menu_company = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Сделать отчет", callback_data=f_m.new(name="Сделать отчет")
            )
        ],
        [
          InlineKeyboardButton(text="Перевести в термины заказчика", callback_data=f_m.new(name="Перевести в термины заказчика"))
        ],
        [
            InlineKeyboardButton(text="Закончить рабочий день", callback_data=f_m.new(name="Закончить рабочий день")
            )
        ]
    ]
)
foreman_start_end_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Начать рабочий день", callback_data=f_m.new(name="Начать рабочий день")
            )
        ],
        [
            InlineKeyboardButton(text="Закончить рабочий день", callback_data=f_m.new(name="Закончить рабочий день")
            )
        ],
    ]
)