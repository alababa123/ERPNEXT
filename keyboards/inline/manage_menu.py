from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.manage_menu_callback import f_m
manage_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Удаление сотрудников", callback_data=f_m.new(name="Удаление сотрудников")
            )
        ],
        [
            InlineKeyboardButton(text="Перевод проекта", callback_data=f_m.new(name="Перевод проекта")
            )
        ],
        [
        InlineKeyboardButton(text="Закончить рабочий день", callback_data=f_m.new(name="Закончить рабочий день"))
        ],
]
)
manage_menu_delete = InlineKeyboardMarkup(
 inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=f_m.new(name="Да")
            )
        ],
        [
            InlineKeyboardButton(text="Нет", callback_data=f_m.new(name="Нет")
            )
        ],
]
)