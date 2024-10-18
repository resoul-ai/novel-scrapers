from .novel_scraper import FichubScraper, Provider, RoyalRoadScraper, Scraper
from .scrapers.fichub import (
    extract_chapters,
    fetch_html_zip,
    get_html_from_zip,
    save_chapters,
)
from .scrapers.royal_road import fetchChapterList, scrapeChapter

__all__ = [
    "extract_chapters",
    "fetch_html_zip",
    "get_html_from_zip",
    "save_chapters",
    "fetchChapterList",
    "scrapeChapter",
    "Provider",
    "Scraper",
    "RoyalRoadScraper",
    "FichubScraper",
]
