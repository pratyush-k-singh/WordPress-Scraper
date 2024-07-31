# Novel PDF Generator

This script fetches chapters from a novel's table of contents (TOC) URL, scrapes the content, and generates PDFs of the novel, splitting it into different books based on user-specified formatting options.

## How It Works

1. **Input TOC URL**: The script prompts you to input the URL of the table of contents of the novel.
2. **Fetch Chapter Links**: It fetches the chapter links from the TOC page.
3. **Scrape Chapter Content**: The script then scrapes the content of each chapter.
4. **Create Indices**: It organizes the chapters into separate books.
5. **User Input for Formatting**: The script prompts you to input PDF formatting options (page size, margins, font size, font name).
6. **Generate PDFs**: It creates separate PDF files for each book.

## Usage

1. Ensure you have the required libraries installed by using the `requirements.txt` file:
    ```sh
    pip install -r requirements.txt
    ```

2. Run the script:
    ```sh
    python novel_pdf_generator.py
    ```

3. Follow the prompts to enter the TOC URL and PDF formatting options.

## Standard Book Format

```sh
Page Width (in.): 8.5
Page Height (in.): 11
Left Margin (in.): 1
Bottom Margin (in.): 1
Font Size: 12
Font Name: Helvetica\


## Output

- The script will create PDF files named `novel_part_1.pdf`, `novel_part_2.pdf`, etc., in the same directory as the script.

## Note on Copyright

**WARNING**: Before using this script to scrape and copy text from any website, ensure you have permission to do so. Many books and their content are protected by copyright law. Unauthorized copying and distribution of copyrighted material is illegal and can lead to severe penalties. Always check if the text is copyrighted and if you have the right to copy it.

## Logging

- The script uses logging to provide information about its progress and any errors that occur.
- Check the console output for logs such as:
  - Chapters fetched successfully.
  - Errors in fetching or scraping chapters.
  - Books and chapters generated for the PDF.
