from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot.texts import t

def language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Русский"), KeyboardButton(text="English")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
def main_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(language, "create_profile"))],
            [KeyboardButton(text=t(language, "edit_profile"))],
            [KeyboardButton(text=t(language, "set_prefs"))],
            [KeyboardButton(text=t(language, "find_matches"))],
            [KeyboardButton(text=t(language, "browse_profiles"))],
            [KeyboardButton(text=t(language, "delete_profile"))],
        ],
        resize_keyboard=True,
    )

def gender_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text=t(language, "gender_girl")),
            KeyboardButton(text=t(language, "gender_boy")),
        ]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def role_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="lead"), KeyboardButton(text="follow"), KeyboardButton(text="both")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def edit_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="name"), KeyboardButton(text="class")],
            [KeyboardButton(text="height"), KeyboardButton(text="role")],
            [KeyboardButton(text="experience"), KeyboardButton(text="availability")],
            [KeyboardButton(text="tempo"), KeyboardButton(text="goals")],
            [KeyboardButton(text="description"), KeyboardButton(text="contact")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def browse_keyboard(index: int, total: int, language: str) -> InlineKeyboardMarkup:
    buttons = []
    nav_buttons = []

    if index > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page:{index - 1}"))
    if index < total - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page:{index + 1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton(text=t(language, "change_class"), callback_data="change_class")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
