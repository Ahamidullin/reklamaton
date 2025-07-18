from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.base import async_session
from models.user import User
from models.character import Character
from models.active_character import ActiveCharacter
from fsm.character_creation import CharacterCreation
from keyboards.inline import (
    creation_method_keyboard, skip_keyboard, preview_keyboard,
    archetype_group_keyboard, archetype_type_keyboard, communication_style_keyboard,
    traits_keyboard, edit_options_keyboard
)
from utils.ai import generate_image_with_deepinfra, upload_to_telegraph

router = Router()

@router.callback_query(lambda c: c.data == "create_character")
async def create_character_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CharacterCreation.choosing_creation_method)
    await callback_query.message.edit_text(
        "Как вы хотите создать персонажа?",
        reply_markup=creation_method_keyboard()
    )
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "creation_prompt", CharacterCreation.choosing_creation_method)
async def creation_prompt_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CharacterCreation.prompt_based_description)
    await callback_query.message.edit_text("Опишите вашего персонажа в одном сообщении. Какой у него характер, как он общается, что любит и ненавидит?")
    await callback_query.answer()

@router.message(CharacterCreation.prompt_based_description)
async def prompt_based_description_handler(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(CharacterCreation.prompt_based_name)
    await message.answer("Отличное описание! Теперь придумайте имя для вашего персонажа.")

@router.message(CharacterCreation.prompt_based_name)
async def prompt_based_name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CharacterCreation.prompt_based_avatar)
    await message.answer(
        "Имя принято! Хотите сгенерировать для него внешность? Если да, отправьте текстовое описание для генерации изображения. "
        "Если нет - нажмите 'Пропустить'.",
        reply_markup=skip_keyboard("skip_avatar_creation")
    )

@router.message(CharacterCreation.prompt_based_avatar)
async def prompt_based_avatar_handler(message: Message, state: FSMContext):
    generating_message = await message.answer("🎨 Генерирую внешность... Это может занять до 2 минут.")
    image_bytes = await generate_image_with_deepinfra(message.text)
    if image_bytes:
        image_url = await upload_to_telegraph(image_bytes)
        if image_url:
            await state.update_data(avatar_url=image_url, avatar_prompt=message.text)
            await generating_message.edit_text("✅ Внешность сгенерирована!")
        else:
            await generating_message.edit_text("❌ Не удалось загрузить изображение. Попробуем без него.")
    else:
        await generating_message.edit_text("❌ Не удалось сгенерировать изображение. Попробуем без него.")

    await state.set_state(CharacterCreation.preview)
    await show_character_preview(message, state)


@router.callback_query(lambda c: c.data == "skip_avatar_creation", CharacterCreation.prompt_based_avatar)
async def skip_avatar_creation_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(avatar_prompt=None)
    await state.set_state(CharacterCreation.preview)
    await callback_query.message.edit_text("Хорошо, пропустим создание аватара. "
                                           "Сейчас я соберу карточку вашего персонажа для предпросмотра.")
    await callback_query.answer()
    await show_character_preview(callback_query.message, state)


async def show_character_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    description = data.get("description")
    avatar_url = data.get("avatar_url")

    # If the description is not directly provided (i.e., constructor-based), generate one.
    if not description:
        archetype = data.get("archetype", "Не указан")
        comm_style = data.get("communication_style", "не указан")
        sarcasm = data.get("sarcasm_level", 1)
        humor = data.get("humor_level", 1)
        flirt = data.get("flirt_level", 1)
        unpredictability = data.get("unpredictability_level", 1)
        black_humor = "Да" if data.get("has_black_humor") else "Нет"

        description = (
            f"<b>Архетип:</b> {archetype}\n"
            f"<b>Стиль общения:</b> {comm_style}\n"
            f"<b>Сарказм:</b> {sarcasm}/5, <b>Юмор:</b> {humor}/5, <b>Флирт:</b> {flirt}/5\n"
            f"<b>Непредсказуемость:</b> {unpredictability}/5, <b>Черный юмор:</b> {black_humor}"
        )

    caption = f"<b>{name}</b>\n\n{description}"

    if avatar_url:
        sent_message = await message.answer_photo(
            photo=avatar_url,
            caption=caption,
            reply_markup=preview_keyboard(),
            parse_mode="HTML"
        )
        # Save the file_id for future use
        await state.update_data(avatar_file_id=sent_message.photo[-1].file_id)
    else:
        await message.answer(
            text=caption,
            reply_markup=preview_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(lambda c: c.data == "save_character", CharacterCreation.preview)
async def save_character_callback(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        # Find or create user
        user_result = await session.execute(select(User).where(User.telegram_id == callback_query.from_user.id))
        user = user_result.scalars().first()
        if not user:
            user = User(telegram_id=callback_query.from_user.id)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        # Create character
        new_character = Character(
            name=data.get("name"),
            description=data.get("description"), # For prompt-based
            avatar_file_id=data.get("avatar_file_id"), # Use file_id now
            user_id=user.id,
            archetype=data.get("archetype"),
            communication_style=data.get("communication_style"),
            sarcasm_level=data.get("sarcasm_level"),
            humor_level=data.get("humor_level"),
            flirt_level=data.get("flirt_level"),
            unpredictability_level=data.get("unpredictability_level"),
            has_black_humor=data.get("has_black_humor")
        )
        session.add(new_character)
        await session.commit()
        await session.refresh(new_character)

        # Set this character as active
        await session.execute(delete(ActiveCharacter).where(ActiveCharacter.user_id == user.id))
        new_active_character = ActiveCharacter(user_id=user.id, character_id=new_character.id)
        session.add(new_active_character)
        await session.commit()
    
    await state.clear()
    await callback_query.message.edit_text(f"Персонаж {new_character.name} сохранен и готов к общению! "
                                           "Все последующие сообщения будут адресованы ему.")
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "edit_character", CharacterCreation.preview)
async def edit_character_callback(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Check if it was a prompt-based creation
    if "description" in data:
        await state.set_state(CharacterCreation.prompt_based_description)
        await callback_query.message.edit_text(
            "Давайте начнем сначала. Опишите вашего персонажа в одном сообщении.",
        )
    else: # It was a constructor-based creation
        await state.set_state(CharacterCreation.constructor_based_archetype_group)
        await callback_query.message.edit_text(
            "Давайте начнем сначала. Выберите группу архетипов:",
            reply_markup=archetype_group_keyboard()
        )
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "creation_constructor", CharacterCreation.choosing_creation_method)
async def creation_constructor_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CharacterCreation.constructor_based_archetype_group)
    await callback_query.message.edit_text(
        "Выберите группу архетипов:",
        reply_markup=archetype_group_keyboard()
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("archetype_group_"), CharacterCreation.constructor_based_archetype_group)
async def archetype_group_callback(callback_query: CallbackQuery, state: FSMContext):
    group = callback_query.data.split("_")[-1]
    await state.update_data(archetype_group=group)
    await state.set_state(CharacterCreation.constructor_based_archetype_type)

    archetype_types = {
        "analysts": ["INTJ", "INTP", "ENTJ", "ENTP"],
        "diplomats": ["INFJ", "INFP", "ENFJ", "ENFP"],
        "sentinels": ["ISTJ", "ISFJ", "ESTJ", "ESFJ"],
        "explorers": ["ISTP", "ISFP", "ESTP", "ESFP"]
    }

    await callback_query.message.edit_text(
        "Выберите конкретный тип:",
        reply_markup=archetype_type_keyboard(archetype_types[group])
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("archetype_type_"), CharacterCreation.constructor_based_archetype_type)
async def archetype_type_callback(callback_query: CallbackQuery, state: FSMContext):
    archetype = callback_query.data.split("_")[-1]
    await state.update_data(archetype=archetype)
    await state.set_state(CharacterCreation.constructor_based_communication_style)

    await callback_query.message.edit_text(
        "Выберите стиль общения:",
        reply_markup=communication_style_keyboard()
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("comm_style_"), CharacterCreation.constructor_based_communication_style)
async def communication_style_callback(callback_query: CallbackQuery, state: FSMContext):
    style = callback_query.data.split("_")[-1]
    await state.update_data(communication_style=style)
    await state.set_state(CharacterCreation.constructor_based_traits)
    
    # Initialize traits with default values
    await state.update_data(
        sarcasm_level=1,
        humor_level=1,
        flirt_level=1,
        unpredictability_level=1,
        has_black_humor=False
    )

    await callback_query.message.edit_text(
        "Настройте черты характера:",
        reply_markup=traits_keyboard()
    )
    await callback_query.answer() 

@router.callback_query(F.data.startswith("trait_"), CharacterCreation.constructor_based_traits)
async def traits_callback(callback_query: CallbackQuery, state: FSMContext):
    action = callback_query.data.split("_")[1]
    
    if action == "continue":
        await state.set_state(CharacterCreation.constructor_based_name)
        await callback_query.message.edit_text("Черты характера настроены! Теперь придумайте имя для вашего персонажа.")
        await callback_query.answer()
        return

    data = await state.get_data()
    trait = callback_query.data.split("_")[-1]
    
    if action == "incr":
        key = f"{trait}_level"
        if data[key] < 5:
            data[key] += 1
    elif action == "decr":
        key = f"{trait}_level"
        if data[key] > 1:
            data[key] -= 1
    elif action == "toggle":
        key = "has_black_humor"
        data[key] = not data[key]

    await state.set_data(data)
    
    await callback_query.message.edit_reply_markup(
        reply_markup=traits_keyboard(
            sarcasm=data.get("sarcasm_level", 1),
            humor=data.get("humor_level", 1),
            flirt=data.get("flirt_level", 1),
            unpredictability=data.get("unpredictability_level", 1),
            black_humor=data.get("has_black_humor", False)
        )
    )
    await callback_query.answer() 

@router.message(CharacterCreation.constructor_based_name)
async def constructor_based_name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CharacterCreation.constructor_based_avatar)
    await message.answer(
        "Имя принято! Хотите сгенерировать для него внешность? Если да, отправьте текстовое описание для генерации изображения. "
        "Если нет - нажмите 'Пропустить'.",
        reply_markup=skip_keyboard("skip_avatar_creation")
    ) 

@router.message(CharacterCreation.constructor_based_avatar)
async def constructor_based_avatar_handler(message: Message, state: FSMContext):
    generating_message = await message.answer("🎨 Генерирую внешность... Это может занять до 2 минут.")
    image_bytes = await generate_image_with_deepinfra(message.text)
    if image_bytes:
        image_url = await upload_to_telegraph(image_bytes)
        if image_url:
            await state.update_data(avatar_url=image_url, avatar_prompt=message.text)
            await generating_message.edit_text("✅ Внешность сгенерирована!")
        else:
            await generating_message.edit_text("❌ Не удалось загрузить изображение. Попробуем без него.")
    else:
        await generating_message.edit_text("❌ Не удалось сгенерировать изображение. Попробуем без него.")
    
    await state.set_state(CharacterCreation.preview)
    await show_character_preview(message, state)

@router.callback_query(lambda c: c.data == "skip_avatar_creation", CharacterCreation.constructor_based_avatar)
async def skip_avatar_creation_constructor_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(avatar_prompt=None)
    await state.set_state(CharacterCreation.preview)
    await callback_query.message.edit_text("Хорошо, пропустим создание аватара. "
                                           "Сейчас я соберу карточку вашего персонажа для предпросмотра.")
    await callback_query.answer()
    await show_character_preview(callback_query.message, state) 

@router.callback_query(F.data.startswith("edit_character_"))
async def edit_character_entry_callback(callback_query: CallbackQuery, state: FSMContext):
    character_id = int(callback_query.data.split("_")[-1])
    async with async_session() as session:
        character = await session.get(Character, character_id)

    if not character:
        await callback_query.answer("Персонаж не найден.", show_alert=True)
        return
        
    # Load character data into FSM
    await state.set_state(CharacterCreation.editing)
    await state.set_data({
        "character_id": character.id,
        "name": character.name,
        "description": character.description,
        "avatar_file_id": character.avatar_file_id,
        "archetype": character.archetype,
        "communication_style": character.communication_style,
        "sarcasm_level": character.sarcasm_level or 1,
        "humor_level": character.humor_level or 1,
        "flirt_level": character.flirt_level or 1,
        "unpredictability_level": character.unpredictability_level or 1,
        "has_black_humor": character.has_black_humor or False
    })

    await callback_query.message.edit_text(
        f"Редактирование персонажа: {character.name}",
        reply_markup=edit_options_keyboard()
    )
    await callback_query.answer() 

@router.callback_query(F.data.startswith("edit_option_"), CharacterCreation.editing)
async def edit_option_callback(callback_query: CallbackQuery, state: FSMContext):
    option = callback_query.data.split("_")[-1]
    
    if option == "name":
        await state.set_state(CharacterCreation.editing_field)
        await state.update_data(editing_what="name")
        await callback_query.message.edit_text("Введите новое имя для персонажа:")
    
    elif option == "avatar":
        await state.set_state(CharacterCreation.editing_field)
        await state.update_data(editing_what="avatar")
        await callback_query.message.edit_text("Отправьте текстовое описание для генерации нового изображения:")
        
    elif option == "description":
        data = await state.get_data()
        # If the character has a text description, it's prompt-based
        if data.get("description"):
            await state.set_state(CharacterCreation.prompt_based_description)
            await callback_query.message.edit_text("Опишите вашего персонажа в одном сообщении:")
        else: # Otherwise, it's constructor-based, restart that flow
            await state.set_state(CharacterCreation.constructor_based_archetype_group)
            await callback_query.message.edit_text("Выберите группу архетипов:", reply_markup=archetype_group_keyboard())
            
    await callback_query.answer()

@router.message(CharacterCreation.editing_field)
async def editing_field_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    editing_what = data.get("editing_what")

    if editing_what == "name":
        await state.update_data(name=message.text)
        await message.answer(f"Имя изменено на: {message.text}")

    elif editing_what == "avatar":
        generating_message = await message.answer("🎨 Генерирую новое изображение... Это может занять до 2 минут.")
        image_bytes = await generate_image_with_deepinfra(message.text)
        if image_bytes:
            # Send the photo to get a file_id
            sent_photo = await message.answer_photo(image_bytes)
            await state.update_data(avatar_file_id=sent_photo.photo[-1].file_id)
            await generating_message.edit_text("✅ Изображение обновлено!")
        else:
            await generating_message.edit_text("❌ Не удалось сгенерировать изображение.")
    
    await state.set_state(CharacterCreation.editing)
    await message.answer("Что еще вы хотите изменить?", reply_markup=edit_options_keyboard()) 

@router.callback_query(F.data == "edit_save", CharacterCreation.editing)
async def edit_save_callback(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    character_id = data.get("character_id")

    if not character_id:
        await callback_query.answer("Ошибка: не найден ID персонажа.", show_alert=True)
        await state.clear()
        return

    async with async_session() as session:
        character = await session.get(Character, character_id)
        if character:
            character.name = data.get("name")
            character.description = data.get("description")
            character.avatar_file_id = data.get("avatar_file_id")
            character.archetype = data.get("archetype")
            character.communication_style = data.get("communication_style")
            character.sarcasm_level = data.get("sarcasm_level")
            character.humor_level = data.get("humor_level")
            character.flirt_level = data.get("flirt_level")
            character.unpredictability_level = data.get("unpredictability_level")
            character.has_black_humor = data.get("has_black_humor")
            await session.commit()
            await callback_query.message.edit_text(f"✅ Изменения для персонажа {character.name} сохранены!")
        else:
            await callback_query.message.edit_text("❌ Не удалось найти персонажа для сохранения.")

    await state.clear()
    await callback_query.answer() 