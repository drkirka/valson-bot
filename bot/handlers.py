from typing import Optional
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import LanguageForm, BrowseForm, MatchBrowseForm
from bot.texts import t
from bot.keyboards import language_keyboard, main_keyboard, browse_keyboard
from bot.database import delete_profile, get_profile, get_profiles_by_class, get_user_language, set_user_language
from bot.profile_handlers import router as profile_router, start_profile, start_edit
from bot.match_handlers import router as match_router, start_prefs, show_matches

router = Router()
router.include_router(profile_router)
router.include_router(match_router)
browse_cache = {}

def clean_text(value: Optional[str]) -> str:
    return (value or "").strip()

def normalize_class_name(value: str) -> str:
    return " ".join(value.split()).upper()

def forget_browse_cache(user_id: int) -> None:
    browse_cache.pop(user_id, None)

async def show_main_menu(message: Message, language: str):
    await message.answer(f"{t(language, 'start')}\n\n{t(language, 'choose_action')}", reply_markup=main_keyboard(language))

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    forget_browse_cache(message.from_user.id)
    await state.set_state(LanguageForm.language)
    await message.answer(t("ru", "choose_language"), reply_markup=language_keyboard())

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    await state.clear()
    forget_browse_cache(message.from_user.id)
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

@router.message(BrowseForm.class_name)
async def browse_profiles_by_class(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    class_name = normalize_class_name(clean_text(message.text))
    profiles = await get_profiles_by_class(class_name)
    if not profiles:
        forget_browse_cache(message.from_user.id)
        await message.answer(t(language, "no_profiles"))
        return
    browse_cache[message.from_user.id] = profiles
    await state.clear()
    await send_profile_page(message, profiles, 0)

async def send_profile_page(message_or_callback, profiles, index: int):
    profile = profiles[index]
    language = await get_user_language(message_or_callback.from_user.id)
    score = ""
    if "match_score" in profile:
        reasons = ", ".join(profile.get("match_reasons", []))
        score = f"\n{t(language, 'score').format(score=profile['match_score'])}\n{t(language, 'match_reasons').format(reasons=reasons)}\n"
    caption = (
        f"{profile['name']}, {profile['class_name']}\n"
        f"{profile['height']} {t(language, 'cm')} | {profile.get('role', 'both')}\n"
        f"{profile.get('experience', '')}\n{profile.get('availability', '')}\n"
        f"{score}\n{profile['description']}\n\n"
        f"{profile['contact']}\n\n"
        f"{t(language, 'page').format(current=index + 1, total=len(profiles))}"
    )
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer_photo(photo=profile["photo_file_id"], caption=caption, reply_markup=browse_keyboard(index, len(profiles), language))
    else:
        await message_or_callback.message.answer_photo(photo=profile["photo_file_id"], caption=caption, reply_markup=browse_keyboard(index, len(profiles), language))

@router.callback_query(F.data.startswith("page:"))
async def change_page(callback: CallbackQuery):
    language = await get_user_language(callback.from_user.id)
    index = int(callback.data.split(":")[1])
    profiles = browse_cache.get(callback.from_user.id)
    if not profiles or index < 0 or index >= len(profiles):
        forget_browse_cache(callback.from_user.id)
        await callback.answer(t(language, "expired_list"), show_alert=True)
        return
    await callback.message.delete()
    await send_profile_page(callback, profiles, index)
    await callback.answer()

@router.callback_query(F.data == "change_class")
async def change_class(callback: CallbackQuery, state: FSMContext):
    language = await get_user_language(callback.from_user.id)
    forget_browse_cache(callback.from_user.id)
    await state.set_state(BrowseForm.class_name)
    await callback.message.answer(t(language, "browse_class"))
    await callback.answer()

@router.message()
async def menu_router(message: Message, state: FSMContext):
    language = await get_user_language(message.from_user.id)
    if message.text == t(language, "create_profile"):
        forget_browse_cache(message.from_user.id)
        await start_profile(message, state)
        return
    if message.text == t(language, "edit_profile"):
        await start_edit(message, state)
        return
    if message.text == t(language, "set_prefs"):
        await start_prefs(message, state)
        return
    if message.text == t(language, "find_matches"):
        matches = await show_matches(message, send_profile_page)
        if matches:
            browse_cache[message.from_user.id] = matches
            await state.set_state(MatchBrowseForm.browsing)
        return
    if message.text == t(language, "browse_profiles"):
        forget_browse_cache(message.from_user.id)
        await state.set_state(BrowseForm.class_name)
        await message.answer(t(language, "browse_class"))
        return
    if message.text == t(language, "delete_profile"):
        existing_profile = await get_profile(message.from_user.id)
        if not existing_profile:
            await message.answer(t(language, "no_profile_to_delete"), reply_markup=main_keyboard(language))
            return
        await delete_profile(message.from_user.id)
        forget_browse_cache(message.from_user.id)
        await message.answer(t(language, "profile_deleted"), reply_markup=main_keyboard(language))
        return
    await show_main_menu(message, language)
