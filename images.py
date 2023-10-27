import os
import fitz
import io

from PIL import Image, ImageDraw, ImageFont
#этот код используется для создания и обработки папок с изображениями
# work with images 
# creating files with all images from pdfs
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

# # creating an image file for each page 
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