import PyPDF2
import re

def convert_pdf_to_text_range(file_path, start_page, end_page):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(start_page-1, end_page):
            text += reader.pages[page].extract_text()
    return text

text_inst_admi= convert_pdf_to_text_range("this.pdf", 1, 45)
text_inst_oper= convert_pdf_to_text_range("oper.pdf", 1, 18)
text_from_inst= convert_pdf_to_text_range("this.pdf", 2, 3)
text_from_oper= convert_pdf_to_text_range("oper.pdf", 2, 2)

def split_text_to_pages(text, pattern):
    pages = re.split(pattern, text)
    pages_dict = {}

    for i, page in enumerate(pages):
        page = page.strip()

        if page:
            pages_dict[i+1] = page

    return pages_dict

#текст ответов "администратор"
pattern_i = r'Руководство администратора\s+Стр\. \d+ из \d+'
pages_dict_i = split_text_to_pages(text_inst_admi, pattern_i)

#текст ответов "оператор"
pattern_o = r'Руководство оператора\s+Стр\. \d+ из \d+'
pages_dict_o = split_text_to_pages(text_inst_oper, pattern_o)

cleaned_text_inst = re.sub(r'\.{2,}', '', text_from_inst)
cleaned_text_oper = re.sub(r'\.{2,}', '', text_from_oper)

def filter_by_pattern(text):
    return "\n".join([line for line in text.split("\n") if re.match(r'^\d+\.\s[^.].*', line)])

filtered_text_i = filter_by_pattern(cleaned_text_inst)
filtered_text_o = filter_by_pattern(cleaned_text_oper)
lines_i = filtered_text_i.split('\n') 
lines_o = filtered_text_o.split('\n')

def process_lines(lines):
    new_lines = []

    for i in range(len(lines)):
        match = re.search(r"(\d+)\s*$", lines[i])  
        if match:
            start_page = int(match.group(1))

            if i < len(lines) - 1: 
                next_match = re.search(r"(\d+)\s*$", lines[i+1]) 
                end_page = int(next_match.group(1)) - 1 if next_match else start_page
            else:
                end_page = start_page

            end_page = max(end_page, start_page)
            text = re.sub(r"^\d+\.\s+", "", lines[i])
            text = re.sub(r"(\d+)\s*$", f"{start_page}-{end_page}", text)
            new_lines.append(text)

    return new_lines

 #текст который берется на кнопки
new_lines_i = process_lines(lines_i)
new_lines_o = process_lines(lines_o)