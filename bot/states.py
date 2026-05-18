from aiogram.fsm.state import State, StatesGroup


class LanguageForm(StatesGroup):
    language = State()


class ProfileForm(StatesGroup):
    gender = State()
    name = State()
    class_name = State()
    height = State()
    photo = State()
    description = State()
    contact = State()


class BrowseForm(StatesGroup):
    class_name = State()
