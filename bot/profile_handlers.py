from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states import ProfileForm, ProfileEditForm
from bot.texts import t
from bot.keyboards import main_keyboard, gender_keyboard, role_keyboard, edit_keyboard
from bot.database import get_user_language, save_profile, get_profile

router = Router()

def s(m):
    return (m.text or '').strip()

def cls(v):
    return ' '.join(v.split()).upper()

def opt(v):
    v = (v or '').strip()
    return '' if v == '-' else v

async def start_profile(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(ProfileForm.gender)
    await message.answer(t(lang, 'choose_gender'), reply_markup=gender_keyboard(lang))

async def start_edit(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if not await get_profile(message.from_user.id):
        await message.answer(t(lang, 'need_profile'), reply_markup=main_keyboard(lang))
        return
    await state.set_state(ProfileEditForm.field)
    await message.answer(t(lang, 'edit_choose'), reply_markup=edit_keyboard(lang))

@router.message(ProfileForm.gender)
async def gender(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text not in [t(lang, 'gender_girl'), t(lang, 'gender_boy')]:
        await message.answer(t(lang, 'choose_gender_button'))
        return
    await state.update_data(gender=message.text)
    await state.set_state(ProfileForm.name)
    await message.answer(t(lang, 'enter_name'))

@router.message(ProfileForm.name)
async def name(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    value = s(message)
    if len(value) < 2 or len(value) > 40:
        await message.answer(t(lang, 'bad_name'))
        return
    await state.update_data(name=value)
    await state.set_state(ProfileForm.class_name)
    await message.answer(t(lang, 'enter_class'))

@router.message(ProfileForm.class_name)
async def class_name(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    value = cls(s(message))
    if len(value) < 1 or len(value) > 20:
        await message.answer(t(lang, 'bad_class'))
        return
    await state.update_data(class_name=value)
    await state.set_state(ProfileForm.height)
    await message.answer(t(lang, 'enter_height'))

@router.message(ProfileForm.height)
async def height(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    try:
        value = int(s(message))
    except ValueError:
        await message.answer(t(lang, 'bad_height_number'))
        return
    if value < 120 or value > 230:
        await message.answer(t(lang, 'bad_height_range'))
        return
    await state.update_data(height=value)
    await state.set_state(ProfileForm.role)
    await message.answer(t(lang, 'enter_role'), reply_markup=role_keyboard(lang))

@router.message(ProfileForm.role)
async def role(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    value = s(message).lower()
    if value not in ['lead', 'follow', 'both']:
        await message.answer(t(lang, 'bad_role'), reply_markup=role_keyboard(lang))
        return
    await state.update_data(role=value)
    await state.set_state(ProfileForm.experience)
    await message.answer(t(lang, 'enter_experience'))

@router.message(ProfileForm.experience)
async def exp(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    value = s(message)
    if len(value) > 40:
        await message.answer(t(lang, 'bad_experience'))
        return
    await state.update_data(experience=value)
    await state.set_state(ProfileForm.availability)
    await message.answer(t(lang, 'enter_availability'))

@router.message(ProfileForm.availability)
async def time(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    value = s(message)
    if len(value) > 100:
        await message.answer(t(lang, 'bad_availability'))
        return
    await state.update_data(availability=value)
    await state.set_state(ProfileForm.tempo)
    await message.answer(t(lang, 'enter_tempo'))

@router.message(ProfileForm.tempo)
async def tempo(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(tempo=opt(s(message)))
    await state.set_state(ProfileForm.goals)
    await message.answer(t(lang, 'enter_goals'))

@router.message(ProfileForm.goals)
async def goals(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(goals=opt(s(message)))
    await state.set_state(ProfileForm.photo)
    await message.answer(t(lang, 'enter_photo'))

@router.message(ProfileForm.photo)
async def photo(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if not message.photo:
        await message.answer(t(lang, 'bad_photo'))
        return
    await state.update_data(photo_file_id=message.photo[-1].file_id)
    await state.set_state(ProfileForm.description)
    await message.answer(t(lang, 'enter_description'))

@router.message(ProfileForm.description)
async def desc(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    value = s(message)
    if len(value) < 5:
        await message.answer(t(lang, 'bad_description_short'))
        return
    if len(value) > 500:
        await message.answer(t(lang, 'bad_description_long'))
        return
    await state.update_data(description=value)
    await state.set_state(ProfileForm.contact)
    await message.answer(t(lang, 'enter_contact'))

@router.message(ProfileForm.contact)
async def contact(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    value = s(message)
    if len(value) < 2 or len(value) > 100:
        await message.answer(t(lang, 'bad_contact'))
        return
    d = await state.get_data()
    await save_profile(message.from_user.id, d['gender'], d['name'], d['class_name'], d['height'], d['photo_file_id'], d['description'], value, d['role'], d['experience'], d['availability'], d['tempo'], d['goals'])
    await state.clear()
    await message.answer(t(lang, 'profile_saved'), reply_markup=main_keyboard(lang))

@router.message(ProfileEditForm.field)
async def edit_field(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    field = s(message).lower()
    if field not in ['name','class','height','role','experience','availability','tempo','goals','description','contact']:
        await message.answer(t(lang, 'bad_edit_field'), reply_markup=edit_keyboard(lang))
        return
    await state.update_data(field=field)
    await state.set_state(ProfileEditForm.value)
    await message.answer(t(lang, 'edit_value'))

@router.message(ProfileEditForm.value)
async def edit_value(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    p = await get_profile(message.from_user.id)
    if not p:
        await state.clear()
        await message.answer(t(lang, 'need_profile'), reply_markup=main_keyboard(lang))
        return
    field = (await state.get_data())['field']
    value = s(message)
    if field == 'class':
        field = 'class_name'
        value = cls(value)
    if field == 'height':
        try:
            value = int(value)
        except ValueError:
            await message.answer(t(lang, 'bad_height_number'))
            return
    if field in ['tempo', 'goals']:
        value = opt(value)
    p[field] = value
    await save_profile(message.from_user.id, p['gender'], p['name'], p['class_name'], p['height'], p['photo_file_id'], p['description'], p['contact'], p['role'], p['experience'], p['availability'], p['tempo'], p['goals'])
    await state.clear()
    await message.answer(t(lang, 'edit_saved'), reply_markup=main_keyboard(lang))
