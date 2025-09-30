import os

from epub2txt import epub2txt


def epub_to_txt_folder(epub_path, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Extract chapters as a list
    chapter_list = epub2txt(epub_path, outputlist=True)

    # Save each chapter to a text file
    for i, chapter_text in enumerate(chapter_list):
        filename = os.path.join(output_folder, f"chapter_{i+1}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(chapter_text)
    print(f"Conversion complete. Files saved to '{output_folder}'")


if __name__ == "__main__":
    input_epub = "/home/arelius/Calibre Library/baurus/Purple Days (ASOIAF Joffrey Timeloop) (AU) (3)/Purple Days (ASOIAF Joffrey Timeloop) (AU) - baurus.epub"
    output_folder = "/home/arelius/books/purple-days-manual"  # Replace with your desired output folder

    epub_to_txt_folder(input_epub, output_folder)
