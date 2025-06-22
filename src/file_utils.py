import os
import re
from fpdf import FPDF
from .config import MAX_MESSAGE_LENGTH

def save_to_pdf(text: str, name: str) -> str:
    """Сохраняет текст в PDF, корректно обрабатывая Markdown (жирный шрифт)."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_regular_path = os.path.join(base_dir, 'assets', 'arial.ttf')
    font_bold_path = os.path.join(base_dir, 'assets', 'arialbd.ttf')
    
    try:
        pdf.add_font('Arial', '', font_regular_path, uni=True)
        pdf.add_font('Arial', 'B', font_bold_path, uni=True)
        pdf.set_font('Arial', '', 11)
    except FileNotFoundError:
        print("!!! ОШИБКА: Файлы шрифтов не найдены в папке src/assets. Пожалуйста, проверьте их наличие.")
        raise RuntimeError("Ошибка конфигурации сервера: не найдены файлы шрифтов.")

    text = text.replace('\u00ad', '')
    
    text = text.replace('**', '*')
    parts = text.split('*')
    
    is_bold = False
    for part in parts:
        if is_bold:
            pdf.set_font('Arial', 'B', 11)
        else:
            pdf.set_font('Arial', '', 11)

        pdf.multi_cell(w=0, h=5, text=part, new_x="LMARGIN", new_y="NEXT")

        is_bold = not is_bold

    file_path = f"{name.replace(' ', '_')}_analysis.pdf"
    pdf.output(file_path)
    return file_path

def split_text(text: str) -> list[str]:
    """Разбивает длинный текст на части, не превышающие лимит Telegram."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]
    
    chunks = []
    current_chunk = ""
    for line in text.split('\n'):
        if len(current_chunk) + len(line) + 1 > MAX_MESSAGE_LENGTH:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line + "\n"
    
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks