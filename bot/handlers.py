from typing import Optional
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import LanguageForm, ProfileForm, BrowseForm
from bot.texts import t
from bot.keyboards import language_keyboard, main_keyboard, gender_keyboard, browse_keyboard
from bot.database import (
    save_profile, delete_profile, get_profile, get_profiles_by_class,
    get_user_language, set_user_language,
)

router = Router()
browse_cache = {}
def txt(value: Optional[str]) -> str:
    return (value or "").strip()
def cls(value: str) -> str:
    return " ".join(value.split()).upper()

def drop_cache(user_id: int) -> None:
    browse_cache.pop(user_id, None)

async def show_main_menu(message: Message, language: str):
    await message.answer(
        f"{t(language, 'start')}\n\n{t(language, 'choose_action')}",
        reply_markup=main_keyboard(language),
    )

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    drop_cache(message.from_user.id)
    await state.set_state(LanguageForm.language)
    await message.answer(t("ru", "choose_language"), reply_markup=language_keyboard())


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    await state.clear()
    drop_cache(message.from_user.id)
    await message.answer(t(language, "cancelled"), reply_markup=main_keyboard(language))
@router.message(LanguageForm.language)
async def process_language(message: Message, state: FSMContext):
    if message.text == "Русский":
        language = "ru"
    elif message.text == "English":
        language = "en"
    else:
        await message.answer(t("ru", "choose_language"), reply_markup=language_keyboard())
        return

    await set_user_language(message.from_user.id, language)
    await state.clear()
    await message.answer(t(language, "language_saved"))
    await show_main_menu(message, language)
@router.message(ProfileForm.gender)
async def process_gender(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    allowed_genders = [t(language, "gender_girl"), t(language, "gender_boy")]
    if message.text not in allowed_genders:
        await message.answer(t(language, "choose_gender_button"))
        return
    await state.update_data(gender=message.text)
    await state.set_state(ProfileForm.name)
    await message.answer(t(language, "enter_name"))

@router.message(ProfileForm.name)
async def process_name(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    name = txt(message.text)
    if len(name) < 2 or len(name) > 40:
        await message.answer(t(language, "bad_name"))
        return
    await state.update_data(name=name)
    await state.set_state(ProfileForm.class_name)
    await message.answer(t(language, "enter_class"))

@router.message(ProfileForm.class_name)
async def process_class(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    class_name = cls(txt(message.text))
    if len(class_name) < 1 or len(class_name) > 20:
        await message.answer(t(language, "bad_class"))
        return
    await state.update_data(class_name=class_name)
    await state.set_state(ProfileForm.height)
    await message.answer(t(language, "enter_height"))

@router.message(ProfileForm.height)
async def process_height(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    try:
        height = int(txt(message.text))
    except ValueError:
        await message.answer(t(language, "bad_height_number"))
        return
    if height < 100 or height > 250:
        await message.answer(t(language, "bad_height_range"))
        return
    await state.update_data(height=height)
    await state.set_state(ProfileForm.photo)
    await message.answer(t(language, "enter_photo"))

@router.message(ProfileForm.photo)
async def process_photo(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    if not message.photo:
        await message.answer(t(language, "bad_photo"))
        return
    await state.update_data(photo_file_id=message.photo[-1].file_id)
    await state.set_state(ProfileForm.description)
    await message.answer(t(language, "enter_description"))

@router.message(ProfileForm.description)
async def process_description(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    description = txt(message.text)
    if len(description) < 5:
        await message.answer(t(language, "bad_description_short"))
        return
    if len(description) > 500:
        await message.answer(t(language, "bad_description_long"))
        return
    await state.update_data(description=description)
    await state.set_state(ProfileForm.contact)
    await message.answer(t(language, "enter_contact"))


@router.message(ProfileForm.contact)
async def process_contact(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    contact = txt(message.text)
    if len(contact) < 2 or len(contact) > 100:
        await message.answer(t(language, "bad_contact"))
        return

    data = await state.get_data()
    await save_profile(
        user_id=message.from_user.id,
        gender=data["gender"],
        name=data["name"],
        class_name=data["class_name"],
        height=data["height"],
        photo_file_id=data["photo_file_id"],
        description=data["description"],
        contact=contact,
    )
    await state.clear()
    drop_cache(message.from_user.id)
    await message.answer(t(language, "profile_saved"), reply_markup=main_keyboard(language))


@router.message(BrowseForm.class_name)
async def browse_profiles_by_class(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    text = txt(message.text)

    if text == t(language, "create_profile"):
        await state.clear()
        drop_cache(message.from_user.id)
        await state.set_state(ProfileForm.gender)
        await message.answer(t(language, "choose_gender"), reply_markup=gender_keyboard(language))
        return

    if text == t(language, "browse_profiles"):
        await state.clear()
        drop_cache(message.from_user.id)
        await state.set_state(BrowseForm.class_name)
        await message.answer(t(language, "browse_class"))
        return

    if text == t(language, "delete_profile"):
        await state.clear()
        existing_profile = await get_profile(message.from_user.id)
        if not existing_profile:
            await message.answer(t(language, "no_profile_to_delete"), reply_markup=main_keyboard(language))
            return
        await delete_profile(message.from_user.id)
        await state.clear()
        drop_cache(message.from_user.id)
        await message.answer(t(language, "profile_deleted"), reply_markup=main_keyboard(language))
        return

    profiles = await get_profiles_by_class(cls(text))
    if not profiles:
        await state.clear()
        drop_cache(message.from_user.id)
        await message.answer(t(language, "no_profiles"), reply_markup=main_keyboard(language))
        return

    browse_cache[message.from_user.id] = profiles
    await state.clear()
    await send_profile_page(message, profiles, 0)

async def send_profile_page(message_or_callback, profiles, index: int):
    profile = profiles[index]
    language = await get_user_language(message_or_callback.from_user.id)
    caption = (
        f"{profile['name']}, {profile['class_name']}\n"
        f"{profile['height']} {t(language, 'cm')}\n\n"
        f"{profile['description']}\n\n"
        f"{profile['contact']}\n\n"
        f"{t(language, 'page').format(current=index + 1, total=len(profiles))}"
    )
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer_photo(
            photo=profile["photo_file_id"],
            caption=caption,
            reply_markup=browse_keyboard(index, len(profiles), language),
        )
    else:
        await message_or_callback.message.answer_photo(
            photo=profile["photo_file_id"],
            caption=caption,
            reply_markup=browse_keyboard(index, len(profiles), language),
        )


@router.callback_query(F.data.startswith("page:"))
async def change_page(callback: CallbackQuery):
    language = await get_user_language(callback.from_user.id)
    index = int(callback.data.split(":")[1])
    profiles = browse_cache.get(callback.from_user.id)
    if not profiles or index < 0 or index >= len(profiles):
        drop_cache(callback.from_user.id)
        await callback.answer(t(language, "expired_list"), show_alert=True)
        return
    await callback.message.delete()
    await send_profile_page(callback, profiles, index)
    await callback.answer()

@router.callback_query(F.data == "change_class")
async def change_class(callback: CallbackQuery, state: FSMContext):
    language = await get_user_language(callback.from_user.id)
    drop_cache(callback.from_user.id)
    await state.set_state(BrowseForm.class_name)
    await callback.message.answer(t(language, "browse_class"))
    await callback.answer()


@router.message()
async def menu_router(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    if message.text == t(language, "create_profile"):
        await state.clear()
        drop_cache(message.from_user.id)
        await state.set_state(ProfileForm.gender)
        await message.answer(t(language, "choose_gender"), reply_markup=gender_keyboard(language))
        return
    if message.text == t(language, "browse_profiles"):
        await state.clear()
        drop_cache(message.from_user.id)
        await state.set_state(BrowseForm.class_name)
        await message.answer(t(language, "browse_class"))
        return
    if message.text == t(language, "delete_profile"):
        await state.clear()
        existing_profile = await get_profile(message.from_user.id)
        if not existing_profile:
            await message.answer(t(language, "no_profile_to_delete"), reply_markup=main_keyboard(language))
            return
        await delete_profile(message.from_user.id)
        await state.clear()
        drop_cache(message.from_user.id)
        await message.answer(t(language, "profile_deleted"), reply_markup=main_keyboard(language))
        return
    await show_main_menu(message, language)
