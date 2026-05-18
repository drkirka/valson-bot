from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import ProfileForm, BrowseForm
from bot.keyboards import main_keyboard, gender_keyboard, browse_keyboard
from bot.database import save_profile, delete_profile, get_profiles_by_class

router = Router()

# user_id -> list of profiles
browse_cache = {}


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здарова. Я помогу найти пару на вальс.\n\n"
        "Выбирай, что делаем:",
        reply_markup=main_keyboard,
    )


@router.message(F.text == "создать / обновить анкету")
async def create_profile(message: Message, state: FSMContext):
    await state.set_state(ProfileForm.gender)
    await message.answer("Выбирай свой пол", reply_markup=gender_keyboard)


@router.message(ProfileForm.gender)
async def process_gender(message: Message, state: FSMContext):
    if message.text not in ["девчонка", "мальчик"]:
        await message.answer("Выбери кнопкой: девчонка или мальчик")
        return

    await state.update_data(gender=message.text)
    await state.set_state(ProfileForm.name)
    await message.answer("Введи свое имя")


@router.message(ProfileForm.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2 or len(name) > 40:
        await message.answer("Имя должно быть от 2 до 40 символов")
        return

    await state.update_data(name=name)
    await state.set_state(ProfileForm.class_name)
    await message.answer("Ты кто с какого? Например: Л, Фил, Им, Физ")


@router.message(ProfileForm.class_name)
async def process_class(message: Message, state: FSMContext):
    class_name = message.text.strip()

    if len(class_name) < 1 or len(class_name) > 20:
        await message.answer("Класс/профиль должен быть от 1 до 20 символов")
        return

    await state.update_data(class_name=class_name)
    await state.set_state(ProfileForm.height)
    await message.answer("Теперь свой рост числом. Например: 169")


@router.message(ProfileForm.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = int(message.text.strip())
    except ValueError:
        await message.answer("Рост надо числом. Например: 169")
        return

    if height < 120 or height > 230:
        await message.answer("Введи нормальный рост от 120 до 230")
        return

    await state.update_data(height=height)
    await state.set_state(ProfileForm.photo)
    await message.answer("Кинь фотку")


@router.message(ProfileForm.photo)
async def process_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer(
            "Это не фотка. Кинь именно фото, не стикер и не текст."
        )
        return

    # Telegram присылает несколько размеров фото. Обычно последний — самый крупный.
    photo_file_id = message.photo[-1].file_id

    await state.update_data(photo_file_id=photo_file_id)
    await state.set_state(ProfileForm.description)
    await message.answer("Опиши себя немного")


@router.message(ProfileForm.description)
async def process_description(message: Message, state: FSMContext):
    description = message.text.strip()

    if len(description) < 5:
        await message.answer("Слишком коротко. Напиши хотя бы пару слов")
        return

    if len(description) > 500:
        await message.answer("Слишком длинно. До 500 символов")
        return

    await state.update_data(description=description)
    await state.set_state(ProfileForm.contact)
    await message.answer(
        "Кинь ссылку на тг/инсту/вк или юзернейм, где с тобой можно связаться"
    )


@router.message(ProfileForm.contact)
async def process_contact(message: Message, state: FSMContext):
    contact = message.text.strip()

    if len(contact) < 2 or len(contact) > 100:
        await message.answer("Контакт выглядит странно. Введи нормально")
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
    await message.answer(
        "Анкета сохранена.",
        reply_markup=main_keyboard,
    )


@router.message(F.text == "удалить мою анкету")
async def remove_profile(message: Message):
    await delete_profile(message.from_user.id)
    await message.answer("Твоя анкета удалена.", reply_markup=main_keyboard)


@router.message(F.text == "смотреть анкеты")
async def browse_profiles_start(message: Message, state: FSMContext):
    await state.set_state(BrowseForm.class_name)
    await message.answer("Какой класс хочешь посмотреть? Например: Л, Фил, Им, Физ")


@router.message(BrowseForm.class_name)
async def browse_profiles_by_class(message: Message, state: FSMContext):
    class_name = message.text.strip()
    profiles = await get_profiles_by_class(class_name)

    if not profiles:
        await message.answer(
            "По этому классу пока нет анкет. Попробуй другой класс."
        )
        return

    browse_cache[message.from_user.id] = profiles
    await state.clear()
    await send_profile_page(message, profiles, 0)


async def send_profile_page(message_or_callback, profiles, index: int):
    profile = profiles[index]

    caption = (
        f"{profile['name']}, {profile['class_name']}\n"
        f"{profile['height']} см\n\n"
        f"{profile['description']}\n\n"
        f"{profile['contact']}\n\n"
        f"Страница {index + 1} из {len(profiles)}"
    )

    if isinstance(message_or_callback, Message):
        await message_or_callback.answer_photo(
            photo=profile["photo_file_id"],
            caption=caption,
            reply_markup=browse_keyboard(index, len(profiles)),
        )
    else:
        await message_or_callback.message.answer_photo(
            photo=profile["photo_file_id"],
            caption=caption,
            reply_markup=browse_keyboard(index, len(profiles)),
        )


@router.callback_query(F.data.startswith("page:"))
async def change_page(callback: CallbackQuery):
    index = int(callback.data.split(":")[1])
    profiles = browse_cache.get(callback.from_user.id)

    if not profiles:
        await callback.answer("Список устарел. Выбери класс заново.", show_alert=True)
        return

    await callback.message.delete()
    await send_profile_page(callback, profiles, index)
    await callback.answer()


@router.callback_query(F.data == "change_class")
async def change_class(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BrowseForm.class_name)
    await callback.message.answer("Какой класс хочешь посмотреть?")
    await callback.answer()