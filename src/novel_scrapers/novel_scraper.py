import logging
import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Type

from novel_scrapers.scrapers.fichub import (
    extract_chapters,
    fetch_html_zip,
    get_html_from_zip,
    save_chapters,
)
from novel_scrapers.scrapers.royal_road import fetchChapterList, scrapeChapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stdout)],
)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class Provider(Enum):
    ROYAL_ROAD = "royal road"
    FICHUB = "fichub"

    @classmethod
    def get(cls, name: str) -> "Provider":
        """
        Get the Site enum value from a string.

        :param name: The name of the site.
        :type name: str
        :return: The corresponding Site enum value.
        :rtype: Site
        """
        return cls(name.lower())


class Scraper:
    @classmethod
    def get_scraper(
        cls, site_name: str
    ) -> Type["RoyalRoadScraper"] | Type["FichubScraper"]:
        """
        Get the appropriate scraper class based on the site name.

        :param site_name: The name of the site to scrape.
        :type site_name: str
        :raises ValueError: If no scraper is available for the given site.
        :return: The scraper class for the specified site.
        :rtype: Type[RoyalRoadScraper] | Type[FichubScraper]
        """
        site = Provider.get(site_name.lower())
        match site:
            case Provider.ROYAL_ROAD:
                return RoyalRoadScraper
            case Provider.FICHUB:
                return FichubScraper
            case _:
                raise ValueError(f"No scraper available for site: {site_name}")


class RoyalRoadScraper:
    def __init__(self, novel_name: str, novel_url: str):
        """
        Initialize the RoyalRoadScraper.

        :param novel_name: The name of the novel.
        :type novel_name: str
        :param novel_url: The URL of the novel on Royal Road.
        :type novel_url: str
        """
        self.novel_name = novel_name
        self.novel_url = novel_url
        self.chapters: Optional[List[dict]] = None

    def __enter__(self) -> "RoyalRoadScraper":
        """
        Context manager entry method. Fetches the chapter list.

        :return: The scraper instance.
        :rtype: RoyalRoadScraper
        """
        self.chapters = fetchChapterList(
            novelName=self.novel_name, novelURL=self.novel_url
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method."""
        # Clean up resources if needed
        pass

    def download(self, output_directory: Path) -> None:
        """
        Download all chapters of the novel.

        :param output_directory: The directory to save the downloaded chapters.
        :type output_directory: Path
        :raises ValueError: If no chapters are available to download.
        """
        if not self.chapters:
            raise ValueError(
                "No chapters to download. Use the context manager to initialize."
            )

        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)

        for chapter in self.chapters:
            file_path = scrapeChapter(
                chapterData=chapter,
                outputDir=str(output_path),
                filename=chapter["name"],
            )
            LOGGER.info(f"Downloaded chapter {chapter['name']} to {file_path}")


class FichubScraper:
    def __init__(self, novel_name: str, novel_url: str):
        """
        Initialize the FichubScraper.

        :param novel_name: The name of the novel.
        :type novel_name: str
        :param novel_url: The URL of the novel on Fichub.
        :type novel_url: str
        """
        self.novel_name = novel_name
        self.novel_url = novel_url
        self.chapters: Optional[List[Tuple[str, str]]] = None

    def __enter__(self) -> "FichubScraper":
        """
        Context manager entry method.

        :return: The scraper instance.
        :rtype: FichubScraper
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method."""
        # Clean up resources if needed
        pass

    def download(self, output_directory: Path) -> None:
        """
        Download all chapters of the novel.

        :param output_directory: The directory to save the downloaded chapters.
        :type output_directory: Path
        :raises ValueError: If no chapters are downloaded.
        """
        output_directory.mkdir(parents=True, exist_ok=True)
        # download the zipped html of the chosen story
        fetch_html_zip(url=self.novel_url, output_directory=output_directory)
        html_file = get_html_from_zip(output_directory)
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        self.chapters = extract_chapters(html_content)

        if not self.chapters:
            raise ValueError("No chapters downloaded.")
        chapters = extract_chapters(html_content)
        save_chapters(chapters, output_directory)
