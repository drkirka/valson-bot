from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states import PreferenceForm
from bot.texts import t
from bot.keyboards import main_keyboard, role_keyboard
from bot.database import get_user_language, get_profile, save_prefs, get_prefs, get_all_profiles
from bot.matching import rank_matches

router = Router()

def text(m):
    return (m.text or '').strip()

def cls(v):
    return ' '.join(v.split()).upper()

def opt(v):
    v = (v or '').strip()
    return '' if v == '-' else v

async def start_prefs(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if not await get_profile(message.from_user.id):
        await message.answer(t(lang, 'need_profile'), reply_markup=main_keyboard(lang))
        return
    await state.set_state(PreferenceForm.preferred_class)
    await message.answer(t(lang, 'pref_class'))

async def show_matches(message: Message, send_page):
    lang = await get_user_language(message.from_user.id)
    profile = await get_profile(message.from_user.id)
    prefs = await get_prefs(message.from_user.id)
    if not profile:
        await message.answer(t(lang, 'need_profile'), reply_markup=main_keyboard(lang))
        return None
    if not prefs:
        await message.answer(t(lang, 'need_prefs'), reply_markup=main_keyboard(lang))
        return None
    me = dict(profile)
    me.update(prefs)
    matches = rank_matches(me, await get_all_profiles())
    if not matches:
        await message.answer(t(lang, 'no_matches'), reply_markup=main_keyboard(lang))
        return None
    await send_page(message, matches, 0)
    return matches

@router.message(PreferenceForm.preferred_class)
async def pref_class(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    value = cls(text(message))
    if len(value) < 1 or len(value) > 20:
        await message.answer(t(lang, 'bad_class'))
        return
    await state.update_data(preferred_class=value)
    await state.set_state(PreferenceForm.preferred_role)
    await message.answer(t(lang, 'pref_role'), reply_markup=role_keyboard(lang))

@router.message(PreferenceForm.preferred_role)
async def pref_role(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    value = text(message).lower()
    if value not in ['lead', 'follow', 'both']:
        await message.answer(t(lang, 'bad_role'), reply_markup=role_keyboard(lang))
        return
    await state.update_data(preferred_role=value)
    await state.set_state(PreferenceForm.height_range)
    await message.answer(t(lang, 'pref_height'))

@router.message(PreferenceForm.height_range)
async def pref_height(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    try:
        a, b = text(message).replace(' ', '').split('-', 1)
        a, b = int(a), int(b)
    except ValueError:
        await message.answer(t(lang, 'bad_height_range_pref'))
        return
    if a < 120 or b > 230 or a > b:
        await message.answer(t(lang, 'bad_height_range_pref'))
        return
    await state.update_data(min_height=a, max_height=b)
    await state.set_state(PreferenceForm.experience)
    await message.answer(t(lang, 'enter_experience'))

@router.message(PreferenceForm.experience)
async def pref_exp(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(experience=text(message))
    await state.set_state(PreferenceForm.availability)
    await message.answer(t(lang, 'enter_availability'))

@router.message(PreferenceForm.availability)
async def pref_time(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(availability=text(message))
    await state.set_state(PreferenceForm.tempo)
    await message.answer(t(lang, 'enter_tempo'))

@router.message(PreferenceForm.tempo)
async def pref_tempo(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(tempo=opt(text(message)))
    await state.set_state(PreferenceForm.goals)
    await message.answer(t(lang, 'enter_goals'))

@router.message(PreferenceForm.goals)
async def pref_goals(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    d = await state.get_data()
    await save_prefs(message.from_user.id, d['preferred_class'], d['preferred_role'], d['min_height'], d['max_height'], d['experience'], d['availability'], d['tempo'], opt(text(message)))
    await state.clear()
    await message.answer(t(lang, 'pref_saved'), reply_markup=main_keyboard(lang))
