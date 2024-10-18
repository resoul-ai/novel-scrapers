import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)

HOME_PAGE_URL: str = "https://www.royalroad.com"
SCRAPE_DELAY: int = 1


def fetchChapterList(
    novelName: str, novelURL: str, chapters: Optional[int] = None
) -> List[Dict[str, str]]:
    """
    Fetch the list of chapters for a given novel from RoyalRoad.

    :param novelName: The name of the novel.
    :type novelName: str
    :param novelURL: The URL of the novel's page on RoyalRoad.
    :type novelURL: str
    :param chapters: The number of chapters to fetch. If None or <= 0, fetch all chapters.
    :type chapters: Optional[int], optional
    :raises ValueError: If the chapter table cannot be found on the page.
    :return: A list of dictionaries containing chapter information.
    :rtype: List[Dict[str, str]]
    """
    LOGGER.info(f"> Fetching chapter links for {novelName}...")

    if HOME_PAGE_URL not in novelURL:  # Support both short-handed and full links
        novelURL = HOME_PAGE_URL + novelURL

    fictionPage = requests.get(novelURL)
    soup = BeautifulSoup(fictionPage.content, "html.parser")
    chapterTable = soup.find("table", {"id": "chapters"})

    if not chapterTable:
        raise ValueError("Could not find chapter table on the page")

    startTime = time.time()
    chapterList = []
    rows = chapterTable.findAll("tr")[1:]  # Skip the header row

    # If chapters is None or <= 0, fetch all chapters
    if chapters is None or chapters <= 0:
        chapters = len(rows)

    for row in rows[:chapters]:
        chapterData = {
            "name": row.find("td").find("a").text.strip(),
            "link": row.find("td").find("a")["href"],
            "date": row.find("td", {"class": "text-right"})
            .find("a")
            .contents[1]["title"],
        }
        chapterList.append(chapterData)

    endTime = time.time()
    LOGGER.info(
        f"Fetched {len(chapterList)} chapters in {endTime - startTime:.2f} seconds"
    )

    return chapterList


def scrapeChapter(
    chapterData: Dict[str, str], outputDir: str, filename: Optional[str] = None
) -> str:
    """
    Scrape the content of a single chapter and save it to a file.

    :param chapterData: A dictionary containing chapter information.
    :type chapterData: Dict[str, str]
    :param outputDir: The directory where the chapter file will be saved.
    :type outputDir: str
    :param filename: The name of the file to save the chapter content. If None, a name will be generated.
    :type filename: Optional[str], optional
    :raises ValueError: If the chapter content cannot be found on the page.
    :raises requests.RequestException: If there's an error fetching the chapter page.
    :raises IOError: If there's an error writing the chapter content to a file.
    :return: The path of the saved chapter file.
    :rtype: str
    """
    HOME_PAGE_URL = "https://www.royalroad.com"

    LOGGER.debug(f"Scraping chapter: {chapterData['name']}")
    LOGGER.debug(f"Chapter URL: {HOME_PAGE_URL + chapterData['link']}")

    clean_chapter_name = "".join(
        x for x in chapterData["name"] if (x.isalnum() or x in "- ")
    )

    if not filename:
        filename = f"{clean_chapter_name}.txt"

    try:
        chapterPage = requests.get(HOME_PAGE_URL + chapterData["link"])
        chapterPage.raise_for_status()  # Raise an error for bad status codes
    except requests.RequestException as e:
        LOGGER.error(f"Failed to fetch chapter page: {str(e)}")
        raise

    soup = BeautifulSoup(chapterPage.content, "html.parser")
    chapterContent = soup.find("div", {"class": "chapter-content"})

    if chapterContent:
        text = chapterContent.get_text(separator="\n", strip=True)

        output_path = Path(outputDir)
        output_path.mkdir(parents=True, exist_ok=True)

        file_path = output_path / filename
        try:
            with file_path.open("w", encoding="utf-8") as out_file:
                out_file.write(text)
            LOGGER.debug(f"Successfully wrote chapter to {file_path}")
            return str(file_path)
        except IOError as e:
            LOGGER.error(f"Failed to write chapter to file: {str(e)}")
            raise
    else:
        LOGGER.error(f"Could not find chapter content for {chapterData['name']}")
        raise ValueError(f"Could not find chapter content for {chapterData['name']}")
