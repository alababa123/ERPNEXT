from aiogram.dispatcher.filters.state import StatesGroup, State

class foreman(StatesGroup):
    job = State()
    start_job = State()
    stop_job = State()
    free_worker = State()
    main_menu = State()
    free_worker_profile = State()
    back = State()
    worker = State()
    worker_profile = State()
    report_temp = State()
    report_temp_profile = State()
    end_job = State()
    activity_worker = State()
    activity_worker_profile = State()
    report_temp_down = State()
