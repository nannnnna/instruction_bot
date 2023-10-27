import logging
import os
import re

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
from text import pages_dict_o
from text import pages_dict_i
from text import new_lines_i
from text import new_lines_o

load_dotenv()
token = os.getenv("token")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher(bot)
button_press_count = {"администратор": 0, "оператор": 0}


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