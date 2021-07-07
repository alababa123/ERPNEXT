from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_reg import reg_callback

end_reg = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="да", callback_data=reg_callback.new(
                bool=True
            )),
            InlineKeyboardButton(text="нет", callback_data=reg_callback.new(
                bool=False
            ))
        ]
    ]

)