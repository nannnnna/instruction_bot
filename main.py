import asyncio
import logging
import sys
import os
from os import getenv

import PyPDF2
import spacy
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("token")
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    # Создание инлайн клавиатуры
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    
    # Добавление 11 пустых кнопок
    button = InlineKeyboardButton(text="Some Text", callback_data="some_data")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])


    # Отправка сообщения с инлайн клавиатурой
    await message.answer(
        f"Hello, {hbold(message.from_user.full_name)}! Выберите раздел инструкции.",
        reply_markup=keyboard
    )


async def main() -> None:
    bot = Bot(token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
