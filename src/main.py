"""
Links are written as json to file for easier reading and writing

Hold in memory first, then write everything at the end checking
if some links were not updated. Simpler and easier to read

dl_links path is generated created relative to this main.py file path

output dl_links separated from src code

URLS CANNOT CHANGE FOR SITES ENTERED. MATCHING IS DONE BASED ON URL
"""
import os
import re
import sys
import requests
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# URLs for each software
urls = {
    'cpuid': 'https://www.cpuid.com/softwares/cpu-z.html',
    'gpuz': 'https://www.techpowerup.com/download/techpowerup-gpu-z/#changelog',
    'wagnardsoft': 'https://www.computerbase.de/downloads/treiber/grafikkarten/display-driver-uninstaller-ddu/',
    'hwi': 'https://www.sac.sk/files.php?d=13&l=H',
    'moreclock': 'https://www.igorslab.de/neue-version-des-morepowertools-mpt-und-finale-des-redbioseditors-rbe-zum-download/',
    'wiztree': 'https://diskanalyzer.com/download'
}

# Common headers for scraping
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def scrape_cpuid(soup, file):
    """Scrape the download link for CPUID (CPU-Z)."""
    download_link_tags = soup.find_all('a', class_='button icon-zip')
    for download_link_tag in download_link_tags:
        if 'english' in download_link_tag.text.lower():
            relative_link = download_link_tag['href']
            full_download_url = f"https://www.cpuid.com/{relative_link}"
            return full_download_url


def scrape_gpuz(soup, file):
    """Scrape the GPU-Z download link."""
    form_action_url = "https://www.techpowerup.com/download/techpowerup-gpu-z/"
    standard_version = soup.find('li', class_='file clearfix expanded')
    input_field = standard_version.find('input', {'name': 'id'})

    if input_field:
        value = input_field['value']
        form_data = {"id": value, "server_id": "25"}
        headers = {
            "Origin": "https://www.techpowerup.com",
            "Referer": "https://www.techpowerup.com/download/techpowerup-gpu-z/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        }

        response = requests.post(
            form_action_url, data=form_data, headers=headers, allow_redirects=False
        )
        if "Location" in response.headers:
            download_link = response.headers["Location"]
            return download_link


def scrape_wagnardsoft(soup, file):
    """Scrape the Wagnardsoft (DDU) download link."""
    form = soup.find("form", class_="download-url__right js-download-launch-form")
    if form:
        input_tag = form.find("input", {"name": "url"})
        if input_tag and "value" in input_tag.attrs:
            form_value = input_tag["value"]
            post_url = "https://www.computerbase.de/downloads/treiber/grafikkarten/display-driver-uninstaller-ddu/"
            payload = {"url": form_value, "direct": "1", "js": "1"}
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
            }

            response = requests.post(post_url, data=payload, headers=headers, allow_redirects=False)
            if "Location" in response.headers:
                download_link = response.headers['Location']
                return download_link


def scrape_hwi(soup, file):
    """Scrape the HWiNFO download link."""
    pattern = r"HWiNFO32/HWiNFO64.*- Portable version of sysinfo program for .*"
    table = soup.find('table', {'width': '90%'})

    if table:
        for tr in table.find_all('tr'):
            if tr.find('td') and re.search(pattern, tr.text):
                download_link = tr.find('a')['href']
                if download_link:
                    return download_link


def scrape_moreclock(soup, file):
    """Scrape the MoreClockTool download link."""
    rows = soup.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 0 and 'MoreClockTool (MCT)' in cells[0].text:
            download_link_tag = cells[3].find('a', href=True)
            if download_link_tag:
                download_link = download_link_tag['href']
                return download_link


def scrape_wiztree(soup, file):
    """Scrape the WizTree download link."""
    download_links = soup.find_all('a', class_='orange btn')
    for link in download_links:
        link_text = link.get_text(strip=True)
        download_url = link['href']
        if 'DOWNLOAD INSTALLER' in link_text:
            if download_url.endswith('.exe'):
                download_link = f"https://diskanalyzer.com/{download_url}"
                return download_link


def strip_chars(a_dict):
    """
    Strip whitespace and other characters
    as well as '+' to make accurate comparisons
    between new and old links
    """
    strips = " \t\n\r+"
    for key, value in a_dict.items():
        a_dict[key] = value.rstrip(strips)
    return a_dict


def dict_differentiate(old_dict: dict, new_dict: dict):
    """
    
    """
    old_dict = strip_chars(old_dict)
    new_dict = strip_chars(new_dict)

    return_dict = {}
    common_keys = old_dict.keys() & new_dict.keys()
    for key in common_keys:
        if old_dict[key] != new_dict[key]:
            return_dict[key] = new_dict[key] + "+"
            logger.info(f"Link updated {new_dict[key]}")
        else:
            return_dict[key] = new_dict[key]
    return_dict.update({k: old_dict[k] for k in old_dict.keys() - new_dict.keys()})
    return_dict.update({k: new_dict[k] for k in new_dict.keys() - old_dict.keys()})
    return return_dict


def main():
    print("*"*20)
    file_name = "dl_links.txt"
    current_script_path = Path(__file__).resolve()
    project_root = current_script_path.parent.parent
    dl_links_path = project_root / file_name
    logs_dir = project_root / "logs"
    log_file = logs_dir / "tq_dl.log"
    print(f"Project Root: {project_root}")
    print(f"Download Links Path: {dl_links_path}")
    print(f"Log File Path: {log_file}")

    # Handle logging
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
    logger.info('Script startup')

    if not dl_links_path.exists():
        dl_links_path.touch()
    
    json_dump = {}
    with open(dl_links_path, 'r+') as file:
        contents = file.read().strip()
        print("*"*20)
        print("Current File Contents: ")
        print(contents)
        print("*"*20)
        try:
            current_file = json.loads(contents) if contents else {}
        except JSONDecodeError as e:
            print("Could Not decode Json")
            print("Likely Invalid JSON format in File. Wiping File")
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
        cleaned_links = dict_differentiate(old_dict=current_file, new_dict=json_dump)
        print(f"New Links to be Written to File: {json_dump}")
        print("Wiping File for new links...")
        file.seek(0)
        file.truncate(0)
        json.dump(cleaned_links, file, indent=4)
        input("Success. Press Enter to exit")
if __name__ == "__main__":
    main()