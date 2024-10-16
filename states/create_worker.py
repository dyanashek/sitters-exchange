from aiogram.fsm.state import State, StatesGroup


class CreateWorker(StatesGroup):
    input_name = State()
    input_phone = State()
    input_passport_photo = State()
    input_selfie = State()
    input_zones = State()
    input_about = State()
    input_min_salary = State()
    input_work_type = State()
    input_notifications = State()
    confirmation = State()
    