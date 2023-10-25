import asyncio
import logging
import sys
import os
import PyPDF2
import re
import fitz
import io

from os import getenv
from aiogram import F
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv
from aiogram.types import CallbackQuery


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
lines_i = filtered_text_i.split('\n') # text for second buttons
lines_o = filtered_text_o.split('\n')
# print(lines_i)
# print(lines_o)
# print(filtered_text_i)
# print(filtered_text_o)
# for page_num, text in enumerate(texts_from_pdf, 1): вывод всего текста с допоплнительной нумерацией страниц
#     print(f"------ Page {page_num} ------")
#     print(text)
#     print("-----------------------------\n")

#work eith image 
def extract_and_save_images_from_pdf_with_pymupdf(pdf_path, output_file):
    pdf_document = fitz.open(pdf_path)
    
    images_to_merge = []
    page_heights = {}  # словарь для хранения высот изображений каждой страницы
    
    y_offset = 0
    for current_page in range(pdf_document.page_count):
        page = pdf_document.load_page(current_page)
        images = page.get_images(full=True)
        
        for image_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            
            image = Image.open(io.BytesIO(image_bytes))
            
            # Добавление пометки о номере страницы
            draw = ImageDraw.Draw(image)
            text = f"Page {current_page + 1}"
            font = ImageFont.truetype("arial.ttf", 15)
            draw.text((10,10), text, font=font, fill=(255,0,0,255))
            
            images_to_merge.append(image)
            y_offset += image.height

        # Обновление словаря границ страницы после добавления всех изображений этой страницы
        page_heights[current_page + 1] = y_offset

    # Объединение всех изображений в одно
    total_height = sum(i.height for i in images_to_merge)
    max_width = max(i.width for i in images_to_merge)
    combined_image = Image.new('RGB', (max_width, total_height))
    
    y_offset = 0
    for im in images_to_merge:
        combined_image.paste(im, (0, y_offset))
        y_offset += im.height

    combined_image.save(output_file)
    return output_file, page_heights

pdf_path = 'this.pdf'
output_file = 'admi_images.png'
image_link, page_heights = extract_and_save_images_from_pdf_with_pymupdf(pdf_path, output_file)
pdf_path_2 = 'oper.pdf'
output_file_2 = 'oper_images.png'
image_link_2, page_heights_2 = extract_and_save_images_from_pdf_with_pymupdf(pdf_path_2, output_file_2)

def extract_images_from_combined_file(image_path, page_number, page_heights, output_folder):
    # Открываем комбинированный файл изображений
    combined_image = Image.open(image_path)

    # Извлекаем изображение для указанной страницы
    top = page_heights[page_number - 1] if page_number > 1 else 0
    bottom = page_heights[page_number]

    extracted_image = combined_image.crop((0, top, combined_image.width, bottom))

    # Сохраняем изображение
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, f"page{page_number}.png")
    extracted_image.save(output_path)

    return output_path

# output_folder = 'admi_images'
# for page_number in range(2, 46):
#     extracted_image_path = extract_images_from_combined_file('C:/Users/79819/Documents/GitHub/instruction_bot/admi_images.png', page_number, page_heights, output_folder)
#     # print(f"Изображение для {page_number} страницы сохранено как: {extracted_image_path}")
    
# output_folder = 'oper_images'
# for page_number in range(2, 46):
#     oper_image_path = extract_images_from_combined_file('C:/Users/79819/Documents/GitHub/instruction_bot/oper_images.png', page_number, page_heights, output_folder)
#     # print(f"Изображение для {page_number} страницы сохранено как: {oper_image_path}")

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="администратор"),
            types.KeyboardButton(text="оператор")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,resize_keyboard=True,
        input_field_placeholder="Выберите роль"
        )
    await message.answer("Какая инструкция вам нужна?", reply_markup=keyboard)
    
    @dp.message(F.text.lower() == "администратор")
    async def admin_handler(message: types.Message):
        kb = [[types.KeyboardButton(text=line)] for line in lines_i]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Выберите инструкцию:", reply_markup=keyboard)
        
    @dp.message(F.text.lower() == "оператор")
    async def operator_handler(message: types.Message):
        kb = [[types.KeyboardButton(text=line)] for line in lines_o]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Выберите инструкцию:", reply_markup=keyboard)
        
        


async def main() -> None:
    bot = Bot(token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
