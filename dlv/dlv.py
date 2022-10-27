# coding: utf-8

import sys
import configparser
import logging
import logging.config
import validators
import json
from datetime import datetime
from youtube_dl import YoutubeDL

# TODO
#  - Add a way to get the status: (different script?)
#      - Is running, cat log, entries in input urls.txt, number of failures, disk check (initial, current and final)
#  - Add disk free space check
#  - Move write_file and loadUrls methods to a utility
#  - Add print usage

# TODO How to override log level to DEBUG on VERBOBSE?
logging.config.fileConfig('logger.ini')
log = logging.getLogger()

# Script variables
EXEC_TIME = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
INPUT_URLS_FILE = 'urls.txt'
SUCCESS = []
FAILURES = []
COUNTER = 0

# Config variables
HOST = None
BACKUP_FOLDER = None
OUTPUT_FOLDER = None


def init() -> None:
    """Initializes script parameters"""
    log.info('Loading DLV config')
    global HOST
    global BACKUP_FOLDER
    global OUTPUT_FOLDER

    config = configparser.ConfigParser()
    config.read('dlv.ini')
    dlv_params = None

    if 'dlv_params' not in config.sections():
        log.error('No dlv_params config found :(')
        sys.exit(1)
    else:
        dlv_params = config['dlv_params']

    HOST = dlv_params.get('host')
    BACKUP_FOLDER = dlv_params.get('backup_folder')
    OUTPUT_FOLDER = dlv_params.get('output_folder')


def load_urls() -> list:
    """Loads a list of URLs contained in urls.txt file."""
    log.info('Loading URLs')
    urls = []

    with open(INPUT_URLS_FILE) as urls_file:
        for line in urls_file:
            url = line.strip()
            if not validators.url(url):
                log.warning(f'Skipping invalid URL: "{url}"')
            elif url in urls:
                log.warning(f'Skipping duplicate URL: "{url}"')
            else:
                urls.append(url)

    return urls


def get_ytdl_opts() -> dict:
    # TODO
    #  - Load YDL_OPTS from an external file
    #  - Make cookiefile dynamic and an optional parameter
    #  - Config number of retries

    log.info('Getting YouTubeDL options')

    opts = {
        'nocheckcertificate': True,
        'format': 'best[ext=mp4]/best',
        'nooverwrites': True,
        'noprogress': True,
        'restrictfilenames': True,
        'writeinfojson': True,
        'writethumbnail': True,
        'writesubtitles': True,
        # TODO get cookies from centralized location
        'cookiefile': 'cookies/youtube.txt',
        # TODO use OUTPUT_FOLDER in outtmpl
        'outtmpl': 'downloads/%(extractor)s/%(title)s - %(id)s.%(ext)s',
        # TODO this agent is to fix a TT issue
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'download_archive': 'dev-archive.txt'  # TODO the host name should be dynamic
    }

    log.debug(opts)

    return opts


def write_file(content, folder: str, filename: str, is_json=False) -> None:
    """Writes an Object to a file system."""
    # TODO - Prepend EXEC_TIME to filename inside write_file rather than outside
    log.info(f'Saving file: {filename}')
    output_text = None

    if is_json:
        # TODO - Add dict type as JSON
        output_text = json.dumps(content, indent=4)
    elif isinstance(content, str):
        output_text = content
    elif isinstance(content, list):
        output_text = '\n'.join(content)
    else:
        log.warn(f'Content type is not recognized: {type(content)}!')
        output_text = content

    with open(f'{folder}/{filename}', 'w', encoding='utf-8') as f:
        f.write(output_text)


# TODO
# def main():
#     print('all starts here')
#
# if __name__ == '__main__':
#     main()


init()

# TODO Check for an input list before loading URLs from file
urls = load_urls()
total_urls = len(urls)
if total_urls < 1:
    log.error('No URLs found :(')
    sys.exit(1)
else:
    log.info(f'{total_urls} unique URLs found')

write_file(urls, BACKUP_FOLDER, f'{EXEC_TIME}-input.txt')

with YoutubeDL(get_ytdl_opts()) as ydl:
    for url in urls:
        COUNTER += 1
        log.info(f"Working on {COUNTER} of {total_urls}: '{url}'")
        try:
            # TODO Refactor this to:
            #  1. Download metadata
            #  2. Determine extractor-specific parameters
            #  3. Download video
            ydl.download([url])
            SUCCESS.append(url)
        except:
            log.error(f"An exception occurred with url '{url}'")
            FAILURES.append(url)

write_file(SUCCESS, BACKUP_FOLDER, f'{EXEC_TIME}-success.txt')
write_file(FAILURES, BACKUP_FOLDER, f'{EXEC_TIME}-failures.txt')

# TODO Improve summary
log.info(f'SUCCESS   {len(SUCCESS)}')
log.info(f'FAILURES  {len(FAILURES)}')
log.info(f'TOTAL     {COUNTER}')
