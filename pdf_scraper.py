import requests
from bs4 import BeautifulSoup
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_chapter_links(toc_url):
    try:
        response = requests.get(toc_url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching TOC URL: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    pattern = re.compile(r'\b(Chapter \d+|Prologue|Epilogue)\b', re.IGNORECASE)
    links = soup.find_all('a', href=True)
    chapter_links = [(link.get_text(strip=True), link['href']) for link in links if pattern.search(link.get_text(strip=True))]
    return chapter_links

def scrape_chapter(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching chapter URL: {e}")
        return ""
    
    soup = BeautifulSoup(response.content, 'html.parser')
    chapter_div = soup.find('div', class_='chapter-content')
    if not chapter_div:
        logging.error(f"Chapter content not found at URL: {url}")
        return ""
    
    return chapter_div.get_text().strip()

def create_indices(chapters):
    indices = []
    current_index = []

    for i, (title, _) in enumerate(chapters):
        if re.search(r'\bEpilogue\b', title, re.IGNORECASE):
            if current_index:
                indices.append(current_index)
                current_index = []
            indices.append([title])  # End of the book
        elif re.search(r'\bChapter \d+\b', title, re.IGNORECASE):
            if i > 0:
                prev_chapter = chapters[i - 1][0]
                current_range = re.findall(r'\d+', title)
                prev_range = re.findall(r'\d+', prev_chapter)
                if current_range and prev_range and int(current_range[0]) != int(prev_range[0]):
                    if current_index:
                        indices.append(current_index)
                        current_index = []
            current_index.append((title, chapters[i][1]))
        elif re.search(r'\bPrologue\b', title, re.IGNORECASE):
            if i > 0 and re.search(r'\bChapter \d+\b', chapters[i - 1][0], re.IGNORECASE):
                if current_index:
                    indices.append(current_index)
                    current_index = []
            current_index.append((title, chapters[i][1]))

    if current_index:
        indices.append(current_index)

    return indices

def get_user_input():
    # Get page size in inches
    page_width = float(input("Enter the page width in inches: ")) * 72
    page_height = float(input("Enter the page height in inches: ")) * 72
    page_size = (page_width, page_height)

    # Get margins in inches
    left_margin = float(input("Enter the left margin in inches: ")) * 72
    bottom_margin = float(input("Enter the bottom margin in inches: ")) * 72
    margins = (left_margin, bottom_margin)

    # Get font size
    font_size = int(input("Enter the font size in points: "))
    
    # Get font name
    font_name = input("Enter the font name: ")

    return page_size, margins, font_size, font_name

def create_pdf(chapters, filename, page_size=letter, margins=(72, 72), font_size=12, font_name='Helvetica'):
    c = canvas.Canvas(filename, pagesize=page_size)
    width, height = page_size
    c.setFont(font_name, font_size)
    
    left_margin, bottom_margin = margins
    right_margin, top_margin = width - left_margin, height - bottom_margin
    
    text_object = c.beginText(left_margin, height - top_margin)
    
    for title, content in chapters:
        c.showPage()
        text_object = c.beginText(left_margin, height - top_margin)
        c.setFont(font_name, font_size)
        
        text_object.textLine(title)
        text_object.textLine('-' * len(title))
        text_object.textLine('')
        
        lines = content.split('\n')
        for line in lines:
            for wrapped_line in wrap_text(line, width - left_margin - right_margin, c, font_size, font_name):
                if text_object.getY() < bottom_margin:
                    c.drawText(text_object)
                    c.showPage()
                    text_object = c.beginText(left_margin, height - top_margin)
                    c.setFont(font_name, font_size)
                text_object.textLine(wrapped_line)
        text_object.textLine('')
        text_object.textLine('')
    
    c.drawText(text_object)
    c.save()

def wrap_text(text, max_width, canvas, font_size, font_name):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if canvas.stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def main():
    toc_url = input("Enter the URL of the table of contents: ")
    chapter_links = get_chapter_links(toc_url)
    
    chapters = [(title, scrape_chapter(link)) for title, link in chapter_links]
    
    indices = create_indices(chapters)
    
    # Print the generated indices and chapters
    book_number = 1
    for section in indices:
        print(f"\nBook {book_number}:")
        for chapter in section:
            if isinstance(chapter, tuple):
                print(f"  -> {chapter[0]}")
        book_number += 1
    
    # Get user input for PDF formatting
    page_size, margins, font_size, font_name = get_user_input()
    
    # Create PDFs based on indices
    for i, section in enumerate(indices):
        create_pdf(section, f'novel_part_{i + 1}.pdf', page_size, margins, font_size, font_name)

if __name__ == "__main__":
    main()
