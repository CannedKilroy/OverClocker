import requests
import re

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