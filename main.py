import asyncio
import logging
import sys
import os
import PyPDF2
import re
import fitz
import io

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from os import getenv
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv


load_dotenv()

token = os.getenv("token")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher(bot)
button_press_count = {"администратор": 0, "оператор": 0}


#text from pdf-files
def convert_pdf_to_text_range(file_path, start_page, end_page):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(start_page-1, end_page):
            text += reader.pages[page].extract_text()
    return text

#all text from files
text_inst_admi= convert_pdf_to_text_range("this.pdf", 1, 45)
text_inst_oper= convert_pdf_to_text_range("oper.pdf", 1, 18)

#text for buttons 
text_from_inst= convert_pdf_to_text_range("this.pdf", 2, 3)
text_from_oper= convert_pdf_to_text_range("oper.pdf", 2, 2)

#convert text to dict for pages
def split_text_to_pages(text, pattern):
    pages = re.split(pattern, text)
    pages_dict = {}

    for i, page in enumerate(pages):
        page = page.strip()

        if page:
            pages_dict[i+1] = page

    return pages_dict

#dict for admin
pattern_i = r'Руководство администратора\s+Стр\. \d+ из \d+'
pages_dict_i = split_text_to_pages(text_inst_admi, pattern_i)

#dict for operator
pattern_o = r'Руководство оператора\s+Стр\. \d+ из \d+'
pages_dict_o = split_text_to_pages(text_inst_oper, pattern_o)


#this is all headers from pages 2-3
cleaned_text_inst = re.sub(r'\.{2,}', '', text_from_inst)
cleaned_text_oper = re.sub(r'\.{2,}', '', text_from_oper)



def filter_by_pattern(text):
    return "\n".join([line for line in text.split("\n") if re.match(r'^\d+\.\s[^.].*', line)])

#this is headers for buttons
filtered_text_i = filter_by_pattern(cleaned_text_inst)
filtered_text_o = filter_by_pattern(cleaned_text_oper)
#this is headers for buttons in dict
lines_i = filtered_text_i.split('\n') 
lines_o = filtered_text_o.split('\n')

def process_lines(lines):
    new_lines = []

    for i in range(len(lines)):
        match = re.search(r"(\d+)\s*$", lines[i])  # Ищем номер страницы в конце строки, учитывая возможные пробелы.

        if match:
            start_page = int(match.group(1))

            if i < len(lines) - 1:  # Если это не последний элемент
                next_match = re.search(r"(\d+)\s*$", lines[i+1])  # Ищем номер страницы в следующей строке, учитывая возможные пробелы.
                end_page = int(next_match.group(1)) - 1 if next_match else start_page
            else:
                end_page = start_page

            # Убедимся, что end_page не меньше, чем start_page
            end_page = max(end_page, start_page)

            # Убираем начальный номер и точку, а также обновляем номера страниц.
            text = re.sub(r"^\d+\.\s+", "", lines[i])
            text = re.sub(r"(\d+)\s*$", f"{start_page}-{end_page}", text)

            new_lines.append(text)

    return new_lines

 #this is final text for buttons
new_lines_i = process_lines(lines_i)
new_lines_o = process_lines(lines_o)

#work with images 
#creating files with all images from pdfs
# def extract_and_save_images_from_pdf_with_pymupdf(pdf_path, output_file):
#     pdf_document = fitz.open(pdf_path)
    
#     images_to_merge = []
#     page_heights = {}  # словарь для хранения высот изображений каждой страницы
    
#     y_offset = 0
#     for current_page in range(pdf_document.page_count):
#         page = pdf_document.load_page(current_page)
#         images = page.get_images(full=True)
        
#         for image_index, img in enumerate(images):
#             xref = img[0]
#             base_image = pdf_document.extract_image(xref)
#             image_bytes = base_image["image"]
            
#             image = Image.open(io.BytesIO(image_bytes))
            
#             # Добавление пометки о номере страницы
#             draw = ImageDraw.Draw(image)
#             text = f"Page {current_page + 1}"
#             font = ImageFont.truetype("arial.ttf", 15)
#             draw.text((10,10), text, font=font, fill=(255,0,0,255))
            
#             images_to_merge.append(image)
#             y_offset += image.height

#         # Обновление словаря границ страницы после добавления всех изображений этой страницы
#         page_heights[current_page + 1] = y_offset

#     # Объединение всех изображений в одно
#     total_height = sum(i.height for i in images_to_merge)
#     max_width = max(i.width for i in images_to_merge)
#     combined_image = Image.new('RGB', (max_width, total_height))
    
#     y_offset = 0
#     for im in images_to_merge:
#         combined_image.paste(im, (0, y_offset))
#         y_offset += im.height

#     combined_image.save(output_file)
#     return output_file, page_heights

# pdf_path = 'this.pdf'
# output_file = 'admi_images.png'
# image_link, page_heights = extract_and_save_images_from_pdf_with_pymupdf(pdf_path, output_file)
# pdf_path_2 = 'oper.pdf'
# output_file_2 = 'oper_images.png'
# image_link_2, page_heights_2 = extract_and_save_images_from_pdf_with_pymupdf(pdf_path_2, output_file_2)

#creating an image file for each page 
# def extract_images_from_combined_file(image_path, page_number, page_heights, output_folder):
#     # Открываем комбинированный файл изображений
#     combined_image = Image.open(image_path)

#     # Извлекаем изображение для указанной страницы
#     top = page_heights[page_number - 1] if page_number > 1 else 0
#     bottom = page_heights[page_number]

#     extracted_image = combined_image.crop((0, top, combined_image.width, bottom))

#     # Сохраняем изображение
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

#     output_path = os.path.join(output_folder, f"page{page_number}.png")
#     extracted_image.save(output_path)

#     return output_path

# output_folder = 'admi_images'
# for page_number in range(2, 46):
#     extracted_image_path = extract_images_from_combined_file('C:/Users/79819/Documents/GitHub/instruction_bot/admi_images.png', page_number, page_heights, output_folder)
#     # print(f"Изображение для {page_number} страницы сохранено как: {extracted_image_path}")
    
# output_folder = 'oper_images'
# for page_number in range(2, 19):
#     oper_image_path = extract_images_from_combined_file('C:/Users/79819/Documents/GitHub/instruction_bot/oper_images.png', page_number, page_heights, output_folder)
#     # print(f"Изображение для {page_number} страницы сохранено как: {oper_image_path}")
#bot
def make_keyboard_from_lines(role, lines):
    keyboard = InlineKeyboardMarkup()
    for i, line in enumerate(lines):
        button = InlineKeyboardButton(line, callback_data=f"{role}_{i}")
        keyboard.add(button)
    return keyboard
# Создаем ReplyKeyboardMarkup
reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_button = KeyboardButton("Администратор")
operator_button = KeyboardButton("Оператор")
reply_keyboard.add(admin_button, operator_button)

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Выберите свою роль:", reply_markup=reply_keyboard)

# Обработчики для выбора роли
@dp.message_handler(lambda message: message.text == "Администратор")
async def admin_choice_handler(message: types.Message):
    keyboard = make_keyboard_from_lines("admin", new_lines_i)
    await message.reply("Выберите элемент:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Оператор")
async def operator_choice_handler(message: types.Message):
    keyboard = make_keyboard_from_lines("operator", new_lines_o)
    await message.reply("Выберите элемент:", reply_markup=keyboard)

# Обработчик CallbackQuery для элементов new_lines_i и new_lines_o
@dp.callback_query_handler(lambda c: c.data.startswith("admin_") or c.data.startswith("operator_"))
async def process_item_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    role, item_index = callback_query.data.split("_")
    item_index = int(item_index)
    
    selected_item = new_lines_i[item_index] if role == "admin" else new_lines_o[item_index]
    print(f"Выбран элемент: {selected_item}")  # Логирование выбранного элемента
    pages_dict = pages_dict_i if role == "admin" else pages_dict_o
    
    # Извлекаем номера страниц из выбранной строки
    match = re.search(r"(\d+)-(\d+)", selected_item)
    if match:
        start_page, end_page = map(int, match.groups())
        
       # Определение папки, в которой нужно искать изображения
        folder_path = "admi_images" if role == "admin" else "oper_images"
        
        # Поиск и отправка файлов, соответствующих номерам страниц
        for page in range(start_page, end_page+1):
            file_path = os.path.join(folder_path, f"page{page}.png")
            if os.path.exists(file_path):
                with open(file_path, 'rb') as photo_file:
                    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo_file)
            else:
                await bot.send_message(callback_query.from_user.id, f"Файл не найден: page{page}.png")
        
        # Извлекаем и объединяем текст со всех страниц в диапазоне
        pages_text = ""
        for page in range(start_page, end_page+1):
            pages_text += pages_dict.get(page, "") + "\n"
        
        # Отправляем текст пользователю
        await bot.send_message(callback_query.from_user.id, pages_text or "Текст отсутствует.")
    else:
        await bot.send_message(callback_query.from_user.id, "Не удалось найти диапазон страниц.")
        

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)