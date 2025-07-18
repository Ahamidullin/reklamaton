import io
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.base import async_session
from models.user import User
from models.active_character import ActiveCharacter
from models.character import Character
from models.message import Message as MessageModel
from utils.ai import get_gemini_response, convert_voice_to_opus, get_text_from_speech

router = Router()

async def process_dialogue(message: Message, text: str):
    """A helper function to process both text and voice-to-text messages."""
    async with async_session() as session:
        # 1. Find the user
        user_result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = user_result.scalars().first()
        if not user:
            await message.answer("Пожалуйста, сначала выберите или создайте персонажа.")
            return

        # 2. Find their active character
        active_char_result = await session.execute(
            select(ActiveCharacter).where(ActiveCharacter.user_id == user.id)
        )
        active_character_relation = active_char_result.scalars().first()
        if not active_character_relation:
            await message.answer("У вас нет активного персонажа. Выберите одного из списка /my_characters.")
            return

        character_id = active_character_relation.character_id
        
        # 3. Save user's message to DB
        user_message = MessageModel(
            user_id=user.id,
            character_id=character_id,
            role="user",
            content=text
        )
        session.add(user_message)
        await session.commit()

        # 4. Get conversation history
        history_result = await session.execute(
            select(MessageModel)
            .where(MessageModel.user_id == user.id, MessageModel.character_id == character_id)
            .order_by(MessageModel.timestamp.asc())
        )
        history = history_result.scalars().all()
        
        api_history = [{"role": msg.role, "content": msg.content} for msg in history]

        character_result = await session.execute(select(Character).where(Character.id == character_id))
        character = character_result.scalars().first()

        # 5. Call Gemini API
        response_text = await get_gemini_response(character, api_history)
        
        # 6. Save model's response to DB
        model_message = MessageModel(
            user_id=user.id,
            character_id=character_id,
            role="model",
            content=response_text
        )
        session.add(model_message)
        await session.commit()

        # 7. Send model's response to user
        await message.answer(response_text)

@router.message(F.text)
async def handle_text_message(message: Message):
    await process_dialogue(message, message.text)

@router.message(F.voice)
async def handle_voice_message(message: Message, bot):
    voice_file = io.BytesIO()
    await bot.download(file=message.voice.file_id, destination=voice_file)
    
    # opus_voice = await convert_voice_to_opus(voice_file) # This step might not be needed if Telegram provides opus directly
    transcribed_text = await get_text_from_speech(voice_file)

    if transcribed_text:
        await process_dialogue(message, transcribed_text)
    else:
        await message.answer("Не удалось распознать речь. Попробуйте еще раз.") 