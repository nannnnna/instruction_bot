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
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("token")

nlp = spacy.load("ru_core_news_sm")

# Конвертация PDF в текст
def convert_pdf_to_text(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.getPage(page).extractText()
    return text

# Поиск фрагмента текста
def find_relevant_excerpt(text, query):
    doc = nlp(text)
    sentences = [sent.string.strip() for sent in doc.sents]
    
    max_similarity = 0
    most_relevant_sentence = ""
    
    for sentence in sentences:
        similarity = nlp(sentence).similarity(nlp(query))
        if similarity > max_similarity:
            max_similarity = similarity
            most_relevant_sentence = sentence
            
    return most_relevant_sentence

text_from_pdf = convert_pdf_to_text("this.pdf")

# Инициализация бота и диспетчера
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}! Введите запрос и я найду для вас информацию в инструкции.")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    user_query = message.text
    response = find_relevant_excerpt(text_from_pdf, user_query)
    
    if response:
        await message.answer(response)
    else:
        await message.answer("Извините, я не нашел подходящей информации по вашему запросу.")


async def main() -> None:
    bot = Bot(token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
