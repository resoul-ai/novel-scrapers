import logging
import os
import re
import zipfile
from pathlib import Path
from typing import List, Tuple

from bs4 import BeautifulSoup
from fichub_cli.utils.fetch_data import FetchData
from fichub_cli.utils.processing import get_format_type

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def extract_chapters(html_content: str) -> List[Tuple[str, str]]:
    """
    Extract chapters from the given HTML content.

    :param html_content: The HTML content of the story.
    :type html_content: str
    :return: A list of tuples containing chapter title and content.
    :rtype: List[Tuple[str, str]]
    """
    soup = BeautifulSoup(html_content, "html.parser")
    chapters = []

    for chapter in soup.find_all("div", id=re.compile("^chap_")):
        title = chapter.find("h2").text

        # Remove navigation elements
        for nav in chapter.find_all("div", class_="chapter_nav"):
            nav.decompose()

        # Remove 'chapter list' link
        chapter_list_link = chapter.find("a", href="#contents-list")
        if chapter_list_link:
            chapter_list_link.decompose()

        # Get the content and clean it up
        content = chapter.get_text(separator="\n", strip=True)

        # Remove A/N (Author's Note) if present
        content = re.sub(r"A/N:.*?\n", "", content, flags=re.DOTALL)

        # Clean up extra newlines
        content = re.sub(r"\n{3,}", "\n\n", content)

        chapters.append((title, content))

    return chapters


def save_chapters(chapters: List[Tuple[str, str]], output_dir: str) -> None:
    """
    Save extracted chapters to individual files in the specified output directory.

    :param chapters: A list of tuples containing chapter title and content.
    :type chapters: List[Tuple[str, str]]
    :param output_dir: The directory where chapter files will be saved.
    :type output_dir: str
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, (title, content) in enumerate(chapters, 1):
        filename = f"chapter_{i:03d}_{sanitize_filename(title)}.txt"
        output_path = os.path.join(output_dir, filename)
        LOGGER.info(f"Downloaded chapter {filename} to {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize the given filename by replacing invalid characters with underscores.

    :param filename: The original filename.
    :type filename: str
    :return: The sanitized filename.
    :rtype: str
    """
    return re.sub(r"[^\w\-_\. ]", "_", filename)


def fetch_html_zip(url: str, output_directory: Path, format_type: str = "html") -> None:
    """
    Fetch the HTML content of a story and save it as a zip file.

    :param url: The URL of the story to fetch.
    :type url: str
    :param output_directory: The directory where the zip file will be saved.
    :type output_directory: Path
    :param format_type: The format type of the content, defaults to "html".
    :type format_type: str, optional
    """
    format_type = get_format_type(format_type)
    fic = FetchData(
        format_type=format_type,
        out_dir=output_directory,
    )
    LOGGER.info(url)
    fic.get_fic_with_url(url)


def find_zip_file(directory: str) -> str:
    """
    Find the first zip file in the given directory.

    :param directory: The directory to search for zip files.
    :type directory: str
    :return: The path to the found zip file, or None if not found.
    :rtype: str
    """
    # we assume one zip per story
    for filename in os.listdir(directory):
        if filename.endswith(".zip"):
            return os.path.join(directory, filename)
    return None


def get_html_from_zip(zip_directory: Path) -> str:
    """
    Extract the HTML file from a zip file in the given directory.

    :param zip_directory: The directory containing the zip file.
    :type zip_directory: Path
    :raises Exception: If no zip file is found in the directory.
    :return: The path to the extracted HTML file.
    :rtype: str
    """
    zip_file = find_zip_file(zip_directory)
    if zip_file:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            # unzip into the same directory the zip file is inside of
            zip_ref.extractall(zip_directory)
    else:
        raise Exception(f"No zip file found in {zip_directory}")

    return zip_file.replace(".zip", ".html")
