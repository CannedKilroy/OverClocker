import os
import sys
import requests
import json
import logging

from logging.handlers import RotatingFileHandler
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
    dict_differentiate
)

from site_logic import (
    scrape_cpuid,
    scrape_gpuz,
    scrape_wagnardsoft,
    scrape_hwi,
    scrape_moreclock,
    scrape_wiztree
)

logger = logging.getLogger(__name__)


def main():
    current_script_path = Path(__file__).resolve()
    project_root = current_script_path.parent.parent

    dl_links_dir = project_root / "output"
    dl_links_path = dl_links_dir / dl_file_name
    logs_dir = project_root / "logs"
    log_file = logs_dir / logger_file_name

    if not dl_links_dir.exists():
        dl_links_dir.mkdir(exist_ok=True)
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
    
    file_handler = RotatingFileHandler(str(log_file),
                                        maxBytes=10240, backupCount=2)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    logger = logging.getLogger() 
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    logger.info('\nScript startup')
    logger.info(f"Project Root: {project_root}")
    logger.info(f"Log File Path: {log_file}")
    logger.info(f"Download Links Path: {dl_links_path}")


    if not dl_links_path.exists():
        dl_links_path.touch()
    
    json_dump = {}
    with open(dl_links_path, 'r+') as file:
        contents = file.read().strip()
        logger.info("Current File Contents: ")
        logger.info(contents)

        # Reset Pointer
        file.seek(0)
        try:
            current_file = json.load(file) if contents else {}
        except JSONDecodeError as e:
            logger.error("Could not decode JSON; likely invalid JSON format in file. Wiping file.")
            file.seek(0)
            file.truncate(0)
            current_file = {}
        
        for key, url in urls.items():
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                if key == 'cpuid':
                    dl_link = scrape_cpuid(soup, file)
                    json_dump[key] = dl_link
                elif key == 'gpuz':
                    dl_link = scrape_gpuz(soup, file)
                    json_dump[key] = dl_link
                elif key == 'wagnardsoft':
                    dl_link = scrape_wagnardsoft(soup, file)
                    json_dump[key] = dl_link
                elif key == 'hwi':
                    dl_link = scrape_hwi(soup, file)
                    json_dump[key] = dl_link
                elif key == 'moreclock':
                    dl_link = scrape_moreclock(soup, file)
                    json_dump[key] = dl_link
                elif key == 'wiztree':
                    dl_link = scrape_wiztree(soup, file)
                    json_dump[key] = dl_link
            else:
                print(f"Failed to retrieve {key}. HTTP status code: {response.status_code}")
        
        # Check links and write to file
        cleaned_links = dict_differentiate(
            old_dict=current_file,
            new_dict=json_dump,
            logger=logger
            )
        logger.info(f"New links to be written: {json_dump}")
        file.seek(0)
        file.truncate(0)
        json.dump(cleaned_links, file, indent=4)
        input("Success. Press Enter to exit")

if __name__ == "__main__":
    main()