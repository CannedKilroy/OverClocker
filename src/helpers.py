# URLs
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

# Strip characters
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


def dict_differentiate(old_dict: dict, new_dict: dict, logger):
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