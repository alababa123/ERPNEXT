from aiogram.dispatcher.filters.state import StatesGroup, State

class manage(StatesGroup):
    start_job = State()
    job = State()
    delete = State()
    choise = State()