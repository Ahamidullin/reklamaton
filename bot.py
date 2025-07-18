import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers import general, character_selection, character_creation, dialogue
from models.engine import create_db_and_tables
from models.user import User
from models.character import Character
from models.message import Message
from models.active_character import ActiveCharacter

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить/перезапустить бота"),
        BotCommand(command="/my_characters", description="Посмотреть моих персонажей")
    ]
    await bot.set_my_commands(commands)

async def main():
    logging.basicConfig(level=logging.INFO)

    await create_db_and_tables()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    await set_bot_commands(bot)

    dp.include_router(general.router)
    dp.include_router(character_selection.router)
    dp.include_router(character_creation.router)
    dp.include_router(dialogue.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 