from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="создать / обновить анкету")],
        [KeyboardButton(text="смотреть анкеты")],
        [KeyboardButton(text="удалить мою анкету")],
    ],
    resize_keyboard=True,
)


gender_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="девчонка"), KeyboardButton(text="мальчик")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


def browse_keyboard(index: int, total: int) -> InlineKeyboardMarkup:
    buttons = []

    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page:{index - 1}"))
    if index < total - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page:{index + 1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([
        InlineKeyboardButton(text="хочу посмотреть другой класс", callback_data="change_class")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)