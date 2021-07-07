from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.foreman_menu_callback import f_m
foreman_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Список свободных рабочих", callback_data=f_m.new(name="Список свободных рабочих")
            )
        ],
        [
            InlineKeyboardButton(text="Список подчиненных", callback_data=f_m.new(name="Список подчиненных")
            )
        ],
        [
            InlineKeyboardButton(text="Список отчетов", callback_data=f_m.new(name="Список отчетов")
            )
        ],
        [
          InlineKeyboardButton(text="Журнал учёта рабочих", callback_data=f_m.new(name="Журнал учёта рабочих")
            )
        ],
        [
            InlineKeyboardButton(text="Закончить рабочий день", callback_data=f_m.new(name="Закончить рабочий день")
            )
        ],
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
