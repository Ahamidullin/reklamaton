from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards.inline import main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать в Фабрику персонажей! Здесь вы можете общаться с готовыми AI-персонажами или создавать своих.\n\n"
                         "Используйте меню ниже или команду /my_characters для быстрого доступа к вашим персонажам.",
                         reply_markup=main_menu())

@router.callback_query(lambda c: c.data == "main_menu")
async def main_menu_callback(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Добро пожаловать в Фабрику персонажей! Здесь вы можете общаться с готовыми AI-персонажами или создавать своих.\n\n"
        "Используйте меню ниже или команду /my_characters для быстрого доступа к вашим персонажам.",
        reply_markup=main_menu()
    )
    await callback_query.answer() 