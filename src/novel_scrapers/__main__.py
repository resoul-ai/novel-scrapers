import logging
import sys
from pathlib import Path
from typing import Union

import click

from novel_scrapers.novel_scraper import Scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stdout)],
)


@click.group()
def cli() -> None:
    """Web Scraper CLI for downloading novels from various sites using a given provider (e.g. Fichub)."""
    pass


@cli.command()
@click.option(
    "--provider",
    type=click.Choice(["royal road", "fichub"], case_sensitive=False),
    required=True,
    help="The provider to scrape from",
)
@click.option("--novel-name", required=True, help="Name of the novel")
@click.option("--novel-url", required=True, help="URL of the novel")
@click.option(
    "--output-dir",
    type=click.Path(),
    default="output",
    help="Output directory for downloaded chapters",
)
def download(
    provider: str, novel_name: str, novel_url: str, output_dir: Union[str, Path]
) -> None:
    """
    Download chapters using the specified provider.

    :param provider: The name of the provider to scrape with (either "royal road" or "fichub").
    :type provider: str
    :param novel_name: The name of the novel to download.
    :type novel_name: str
    :param novel_url: The URL of the novel to download.
    :type novel_url: str
    :param output_dir: The directory where downloaded chapters will be saved.
    :type output_dir: Union[str, Path]
    """
    scraper_class = Scraper.get_scraper(provider)
    output_path = Path(output_dir)

    with scraper_class(novel_name, novel_url) as scraper:
        try:
            scraper.download(output_path)
            click.echo(f"Successfully downloaded chapters to {output_path}")
        except Exception as e:
            click.echo(f"Error occurred while downloading: {str(e)}", err=True)


if __name__ == "__main__":
    cli()
