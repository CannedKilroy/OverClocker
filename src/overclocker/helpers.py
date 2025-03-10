import logging
from logging.handlers import RotatingFileHandler
import json
from json.decoder import JSONDecodeError

# Open and return file
def open_file(dl_links_path, logger):
    with open(dl_links_path, 'r+') as file:
        contents = file.read().strip()
        logger.debug("Current File Contents: ")
        logger.debug(contents)
        file.seek(0)
        try:
            current_file = json.load(file) if contents else {}
        except JSONDecodeError as e:
            logger.error("Could not decode JSON; likely invalid JSON format in file. Wiping file.")
            file.seek(0)
            file.truncate(0)
            current_file = {}
    return current_file, file

def write_contents(dl_links_path, contents):
    with open(dl_links_path, "r+") as file:
        json.dump(contents, file, indent=4)

def clear_file(dl_links_path, logger):
    with open(dl_links_path, 'w') as file:
        file.truncate(0)
        logger.info("File cleared.")

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
    print(a_dict)
    return a_dict


# Create files
def create_files(main_script_path, dl_file_name, logger_file_name):
    project_root = main_script_path.parent.parent.parent

    dl_links_dir = project_root / "output"
    dl_links_path = dl_links_dir / dl_file_name
    logs_dir = project_root / "logs"
    log_file_path = logs_dir / logger_file_name

    if not dl_links_dir.exists():
        dl_links_dir.mkdir(exist_ok=True)
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
    return log_file_path, dl_links_path


def setup_logger(log_file_path, level=logging.INFO):
    file_handler = RotatingFileHandler(str(log_file_path), maxBytes=10240, backupCount=2)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(level)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    return root_logger