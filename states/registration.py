from aiogram.dispatcher.filters.state import StatesGroup, State


class registration(StatesGroup):
    fio = State()
    phone = State()
    photo_mes = State()
    passport = State()
    check = State()
    passport_mes = State()
    photo = State()

class registration_foreman(StatesGroup):
    fio = State()
    phone = State()
    photo_mes = State()
    passport = State()
    check = State()
    passport_mes = State()
    photo = State()