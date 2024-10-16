from aiogram.fsm.state import State, StatesGroup


class CreateJob(StatesGroup):
    input_zones = State()
    input_description = State()
    input_min_salary = State()
    input_work_type = State()
    input_notifications = State()
    input_confirmation = State()
    