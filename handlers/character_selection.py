from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models.base import async_session
from models.character import Character
from models.user import User
from models.active_character import ActiveCharacter
from keyboards.inline import character_list_keyboard, character_card_keyboard, confirm_delete_keyboard, main_menu

router = Router()

@router.callback_query(lambda c: c.data == "select_character")
async def select_character_callback(callback_query: CallbackQuery):
    async with async_session() as session:
        result = await session.execute(select(Character).where(Character.is_premade == True))
        premade_characters = result.scalars().all()

    if premade_characters:
        await callback_query.message.edit_text(
            "Выберите одного из готовых персонажей:",
            reply_markup=character_list_keyboard(premade_characters)
        )
    else:
        await callback_query.message.edit_text("К сожалению, готовых персонажей пока нет.")
        
    await callback_query.answer()

@router.callback_query(F.data.startswith("character_"))
async def show_character_card_callback(callback_query: CallbackQuery):
    character_id = int(callback_query.data.split("_")[1])
    async with async_session() as session:
        result = await session.execute(select(Character).where(Character.id == character_id))
        character = result.scalars().first()

    if character:
        description = character.description
        if not description:
            type_names_ru = {
                "INTJ": "Архитектор", "INTP": "Логик", "ENTJ": "Командир", "ENTP": "Полемист",
                "INFJ": "Заступник", "INFP": "Посредник", "ENFJ": "Протагонист", "ENFP": "Активист",
                "ISTJ": "Логист", "ISFJ": "Защитник", "ESTJ": "Менеджер", "ESFJ": "Консул",
                "ISTP": "Виртуоз", "ISFP": "Авантюрист", "ESTP": "Предприниматель", "ESFP": "Артист"
            }
            archetype_code = character.archetype or "Не указан"
            archetype_ru = type_names_ru.get(archetype_code, archetype_code)
            comm_style = character.communication_style or "не указан"
            sarcasm = character.sarcasm_level or 1
            humor = character.humor_level or 1
            flirt = character.flirt_level or 1
            unpredictability = character.unpredictability_level or 1
            black_humor = "Да" if character.has_black_humor else "Нет"

            description = (
                f"<b>Архетип:</b> {archetype_ru}\n"
                f"<b>Стиль общения:</b> {comm_style}\n"
                f"<b>Сарказм:</b> {sarcasm}/5, <b>Юмор:</b> {humor}/5, <b>Флирт:</b> {flirt}/5\n"
                f"<b>Безумие:</b> {unpredictability}/5, <b>Черный юмор:</b> {black_humor}"
            )

        if character.avatar_file_id:
            await callback_query.message.answer_photo(
                photo=character.avatar_file_id,
                caption=f"<b>{character.name}</b>\n\n{description}",
                reply_markup=character_card_keyboard(character.id),
                parse_mode="HTML"
            )
            await callback_query.message.delete()
        else:
            await callback_query.message.edit_text(
                f"<b>{character.name}</b>\n\n{description}",
                reply_markup=character_card_keyboard(character.id),
                parse_mode="HTML"
            )
    else:
        await callback_query.message.edit_text("Персонаж не найден.")
    
    await callback_query.answer() 

@router.callback_query(F.data.startswith("delete_character_"))
async def delete_character_callback(callback_query: CallbackQuery):
    character_id = callback_query.data.split("_")[2]
    
    # Send new message with confirmation
    await callback_query.message.answer(
        text="Вы уверены, что хотите удалить этого персонажа? Это действие необратимо.",
        reply_markup=confirm_delete_keyboard(character_id)
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_callback(callback_query: CallbackQuery):
    character_id = int(callback_query.data.split("_")[2])
    
    async with async_session() as session:
        # First, delete from active_character if it's there
        await session.execute(delete(ActiveCharacter).where(ActiveCharacter.character_id == character_id))
        
        # Then, delete the character itself
        await session.execute(delete(Character).where(Character.id == character_id))
        await session.commit()

    # Send new message about successful deletion
    await callback_query.message.answer("Персонаж успешно удален!")
    
    # Show updated character list
    async with async_session() as session:
        # Find user
        user_result = await session.execute(select(User).where(User.telegram_id == callback_query.from_user.id))
        user = user_result.scalars().first()
        
        user_characters = []
        if user:
            # Get user-created characters
            user_char_result = await session.execute(select(Character).where(Character.user_id == user.id))
            user_characters = user_char_result.scalars().all()

        # Get premade characters
        premade_char_result = await session.execute(select(Character).where(Character.is_premade == True))
        premade_characters = premade_char_result.scalars().all()

        all_characters = user_characters + premade_characters

    if all_characters:
        await callback_query.message.answer(
            "Ваши персонажи:",
            reply_markup=character_list_keyboard(all_characters)
        )
    else:
        await callback_query.message.answer(
            "У вас больше нет созданных персонажей. Вы можете выбрать из готовых или создать нового.",
            reply_markup=main_menu()
        )
    
    await callback_query.answer()


@router.message(Command("my_characters"))
async def my_characters_command(message: Message):
    async with async_session() as session:
        # Find user
        user_result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = user_result.scalars().first()
        
        user_characters = []
        if user:
            # Get user-created characters
            user_char_result = await session.execute(select(Character).where(Character.user_id == user.id))
            user_characters = user_char_result.scalars().all()

        # Get premade characters
        premade_char_result = await session.execute(select(Character).where(Character.is_premade == True))
        premade_characters = premade_char_result.scalars().all()

        all_characters = user_characters + premade_characters

    if all_characters:
        await message.answer(
            "Выберите персонажа, чтобы сделать его активным:",
            reply_markup=character_list_keyboard(all_characters)
        )
    else:
        await message.answer("У вас пока нет созданных персонажей. Вы можете выбрать из готовых или создать нового.")

@router.callback_query(F.data.startswith("start_dialogue_"))
async def start_dialogue_callback(callback_query: CallbackQuery):
    character_id = int(callback_query.data.split("_")[2])
    async with async_session() as session:
        # Get character info
        result = await session.execute(select(Character).where(Character.id == character_id))
        character = result.scalars().first()
        
        if not character:
            await callback_query.message.answer("Персонаж не найден.")
            await callback_query.answer()
            return

        # Find or create user
        user_result = await session.execute(select(User).where(User.telegram_id == callback_query.from_user.id))
        user = user_result.scalars().first()
        if not user:
            user = User(telegram_id=callback_query.from_user.id)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        # Remove any existing active character entry for this user
        await session.execute(delete(ActiveCharacter).where(ActiveCharacter.user_id == user.id))
        
        # Set the new active character
        new_active_character = ActiveCharacter(user_id=user.id, character_id=character_id)
        session.add(new_active_character)
        await session.commit()

        # Generate character description if not exists
        description = character.description
        if not description:
            type_names_ru = {
                "INTJ": "Архитектор", "INTP": "Логик", "ENTJ": "Командир", "ENTP": "Полемист",
                "INFJ": "Заступник", "INFP": "Посредник", "ENFJ": "Протагонист", "ENFP": "Активист",
                "ISTJ": "Логист", "ISFJ": "Защитник", "ESTJ": "Менеджер", "ESFJ": "Консул",
                "ISTP": "Виртуоз", "ISFP": "Авантюрист", "ESTP": "Предприниматель", "ESFP": "Артист"
            }
            archetype_code = character.archetype or "Не указан"
            archetype_ru = type_names_ru.get(archetype_code, archetype_code)
            comm_style = character.communication_style or "не указан"
            sarcasm = character.sarcasm_level or 1
            humor = character.humor_level or 1
            flirt = character.flirt_level or 1
            unpredictability = character.unpredictability_level or 1
            black_humor = "Да" if character.has_black_humor else "Нет"

            description = (
                f"<b>Архетип:</b> {archetype_ru}\n"
                f"<b>Стиль общения:</b> {comm_style}\n"
                f"<b>Сарказм:</b> {sarcasm}/5, <b>Юмор:</b> {humor}/5, <b>Флирт:</b> {flirt}/5\n"
                f"<b>Безумие:</b> {unpredictability}/5, <b>Черный юмор:</b> {black_humor}"
            )

        # Send confirmation message
        confirmation_text = (
            f"✨ <b>Диалог начат с персонажем:</b>\n\n"
            f"<b>{character.name}</b>\n\n"
            f"{description}\n\n"
            f"💬 Теперь все ваши сообщения будут адресованы этому персонажу.\n"
            f"🔄 Чтобы сменить персонажа, используйте команду /my_characters"
        )

        if character.avatar_file_id:
            await callback_query.message.answer_photo(
                photo=character.avatar_file_id,
                caption=confirmation_text,
                parse_mode="HTML"
            )
        else:
            await callback_query.message.answer(
                text=confirmation_text,
                parse_mode="HTML"
            )

    await callback_query.answer() 