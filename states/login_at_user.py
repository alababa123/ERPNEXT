from aiogram.dispatcher.filters.state import  StatesGroup, State

class user_status(StatesGroup):
    logined = State()