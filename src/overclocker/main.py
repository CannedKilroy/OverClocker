import os
import sys
import requests
import json
import logging

from pathlib import Path
from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup

from config import (
    urls,
    headers,
    dl_file_name,
    logger_file_name
)

from helpers import (
    strip_chars,
    create_files,
    setup_logger,
    open_file,
    clear_file,
    write_contents
)

from site_logic import (
scraper_factory
)

logger = logging.getLogger(__name__)


def main():
    main_script_path = Path(__file__).resolve()
    log_file_path, dl_links_path = create_files(
        main_script_path,
        dl_file_name,
        logger_file_name
        )
    setup_logger(log_file_path)

    logger.info('\nScript startup')
    if not dl_links_path.exists():
        dl_links_path.touch()
    
    current_file, file = open_file(dl_links_path, logger)
    json_dump = {}

    for url_key, url in urls.items():
        scraper = scraper_factory(url)
        response = scraper.get_response(url, headers=headers)
        if response.status_code == 200:
            soup = scraper.get_soup()
            dl_link = scraper.scrape(soup)
            # Need to do comparison
            if url_key in current_file:
                old_link = current_file[url_key]
                cleaned_link = scraper.comparison(new_link=dl_link, old_link=old_link)
                json_dump[url_key] = cleaned_link
            # Don't need to do comparison
            else:
                json_dump[url_key] = dl_link
        else:
            # Log Error
            print(f"Failed to retrieve {url_key}. HTTP status code: {response.status_code}")

    logger.debug(f"New links to be written: {json_dump}")
    clear_file(dl_links_path, logger)
    write_contents(dl_links_path, json_dump)
    input("Success. Press Enter to exit")

if __name__ == "__main__":
    main()