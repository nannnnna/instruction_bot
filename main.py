import asyncio
import logging
import sys
import os
import PyPDF2
import re

from os import getenv
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

#text and image from pdf 

def convert_pdf_to_text_range(file_path, start_page, end_page):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(start_page-1, end_page): # индексация страниц начинается с 0
            text += reader.pages[page].extract_text()
    return text

text_from_inst= convert_pdf_to_text_range("this.pdf", 2, 3)
text_from_oper= convert_pdf_to_text_range("oper.pdf", 2, 2)
# Удаление последовательности точек
cleaned_text_inst = re.sub(r'\.{2,}', '', text_from_inst)
cleaned_text_oper = re.sub(r'\.{2,}', '', text_from_oper)
# print(cleaned_text)
# Функция для фильтрации текста по заданному шаблону
def filter_by_pattern(text):
    return "\n".join([line for line in text.split("\n") if re.match(r'^\d+\.\s[^.].*', line)])

filtered_text_i = filter_by_pattern(cleaned_text_inst)
filtered_text_o = filter_by_pattern(cleaned_text_oper)
print(filtered_text_i)
print(filtered_text_o)
# for page_num, text in enumerate(texts_from_pdf, 1): вывод всего текста с допоплнительной нумерацией страниц
#     print(f"------ Page {page_num} ------")
#     print(text)
#     print("-----------------------------\n")


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    
    # Разбиваем текст на строки
    lines_i = filtered_text_i.split('\n')
    lines_o = filtered_text_o.split('\n')
    
    # Создание инлайн клавиатуры
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    
    # Добавление кнопок на основе первых 22 строк
    for i in range(22):
        if i < len(lines_i):
            text_i = lines_i[i]
        else:
            text_i = ""
        
        if i < len(lines_o):
            text_o = lines_o[i]
        else:
            text_o = ""

        button_i = InlineKeyboardButton(text=text_i, callback_data=f"button_i_{i}")
        button_o = InlineKeyboardButton(text=text_o, callback_data=f"button_o_{i}")

        keyboard.inline_keyboard.append([button_i, button_o])


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
