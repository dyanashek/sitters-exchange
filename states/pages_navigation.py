from aiogram.fsm.state import State, StatesGroup


class PageNavigation(StatesGroup):
    page_navigation = State()
    