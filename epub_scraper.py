import requests
from bs4 import BeautifulSoup
from ebooklib import epub

# Global variables
book, currentBookTitle, currentBookNumber = None, "", 0
spine = ["nav"]
books = [[] for _ in range(7)]  # List of lists to hold chapters for each book
chapter_count = 0

def initializeEpubMetadata(book_number):
    book = epub.EpubBook()
    book.set_title(f"A Practical Guide To Evil - Book {book_number}")
    book.set_cover(content="APGTE_front.png", file_name="APGTE_front.png")
    book.add_author("ErraticErrata")
    return book

def main():
    print("Enter the URL for the Table of Contents:")
    URLTableOfContents = input().strip()

    # Access Table of Contents
    page = requests.get(URLTableOfContents)
    soup = BeautifulSoup(page.content, "html.parser")  # Table of Contents
    entryResults = soup.find("div", class_="entry-content")

    if not entryResults:
        entryResults = soup.find("div", class_="post-content")  # Fallback for different WordPress site format

    for child in entryResults.find_all(recursive=False):
        if child.name == 'h2':  # Book Number
            global currentBookNumber, currentBookTitle
            currentBookNumber += 1
            currentBookTitle = child.text + " — "
        elif child.name == 'ul':  # Get all chapters of a Book Number, then extract content each
            iterateChapters(child)

    print("Generating EPUB files...")
    for i in range(7):
        if books[i]:
            generateBook(i + 1, books[i])
    print("Epub files have been generated!")

def iterateChapters(chapters):
    chaptersSoup = BeautifulSoup(str(chapters), "html.parser")  # Contains a list (not the Python kind of list) of chapters of a given book number

    for chapter in chaptersSoup.find_all("li"):
        if not chapter.string:  # Book 2 has an extra empty CSS tag as the first list element, filter it out
            continue
        
        chapterSoup = BeautifulSoup(str(chapter), "html.parser")
        currentChapterTitle = currentBookTitle + chapterSoup.find('a').text  # Get Chapter Title
        url = chapterSoup.find('a')['href']  # Get URL of Chapter
        extractChapter(url, currentChapterTitle)  # Extract content

def extractChapter(url, currentChapterTitle):
    global chapter_count, currentBookNumber
    chapterPage = requests.get(url)  # Visit the Chapter page
    chapterSoup = BeautifulSoup(chapterPage.content, "html.parser")  # Chapter page HTML content

    # Proceed to extract the text of the chapter
    content = chapterSoup.find("div", class_="entry-content")  # Chapter main text body
    if not content:
        content = chapterSoup.find("article")  # Fallback for different WordPress site format

    for s in chapterSoup.select("div[id^='jp-post-flair']"): 
        s.extract()  # Remove footer buttons
    appendChapterToBook(content, currentChapterTitle)

def appendChapterToBook(content, currentChapterTitle):
    global chapter_count, books, currentBookNumber
    epubChapter = epub.EpubHtml(title=currentChapterTitle, file_name=f"{chapter_count}.xhtml", lang='en')
    epubChapter.content = f"<h2>{currentChapterTitle}</h2>" + str(content).replace('<div class="entry-content">\n', "").replace('\n </div>', "")

    books[currentBookNumber - 1].append(epubChapter)
    chapter_count += 1
    print(currentChapterTitle + " OK!")

def generateBook(book_number, chapters):
    book = initializeEpubMetadata(book_number)
    spine = ["nav"] + chapters
    toc = [(epub.Section(f'Book {book_number}'), chapters)]

    for chapter in chapters:
        book.add_item(chapter)
    
    book.spine = spine
    book.toc = toc

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(f'A Practical Guide To Evil - Book {book_number}.epub', book, {})

if __name__ == "__main__": 
    main()
