from aiogram.fsm.state import State, StatesGroup


class CreateReview(StatesGroup):
    rate = State()
    review = State()
    confirmation = State()
    