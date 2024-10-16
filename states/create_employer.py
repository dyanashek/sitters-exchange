from aiogram.fsm.state import State, StatesGroup


class CreateEmployer(StatesGroup):
    input_name = State()
    input_phone = State()
    