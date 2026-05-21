from aiogram.fsm.state import State, StatesGroup

class LanguageForm(StatesGroup):
    language = State()

class ProfileForm(StatesGroup):
    gender = State()
    name = State()
    class_name = State()
    height = State()
    role = State()
    experience = State()
    availability = State()
    tempo = State()
    goals = State()
    photo = State()
    description = State()
    contact = State()

class ProfileEditForm(StatesGroup):
    field = State()
    value = State()

class PreferenceForm(StatesGroup):
    preferred_class = State()
    preferred_role = State()
    height_range = State()
    experience = State()
    availability = State()
    tempo = State()
    goals = State()

class MatchBrowseForm(StatesGroup):
    browsing = State()

class BrowseForm(StatesGroup):
    class_name = State()
