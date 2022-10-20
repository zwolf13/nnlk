# coding: utf-8

import sys
import logging
import validators
import json
from datetime import datetime
import youtube_dl

# TODO
#  - Move all the logging config to a file
#  - Add output format to StreamHandler
#  - Add print usage
#  - Add a way to get the status: (different script?)
#      - Is running, cat log, entries in input urls.txt, number of failures, disk check (initial, current and final)
#  - Make cookiefile dynamic and an optional parameter
#  - Config number of retries
#  - Add disk free space check
#  - Add input URL validation
#  - Add summary
#  - Move write_file and loadUrls methods to a utility

logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', filename='logs/dlv.log', encoding='utf-8', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

INPUT_URLS_FILE = 'urls.txt'
BACKUP_FOLDER = 'backups'
EXEC_TIME = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")

YDL_OPTS = {
    'nocheckcertificate': True,
    'format': 'best[ext=mp4]/best',
    'nooverwrites': True,
    'noprogress': True,
    'restrictfilenames': True,
    'writeinfojson': True,
    'writethumbnail': True,
    'writesubtitles': True,
    'cookiefile': 'cookies/youtube.txt',
    'outtmpl': 'downloads/%(extractor)s/%(title)s - %(id)s.%(ext)s',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'download_archive': 'dev-archive.txt'  # TODO the host name should be dynamic
}

def loadUrls() -> list:
    """
    Loads a list of URLs contained in urls.txt file
    """
    logging.info('Loading URLs...')
    urls = []
    with open(INPUT_URLS_FILE) as urls_file:
        for line in urls_file:
            url = line.strip()
            if not validators.url(url):
                logging.warning(f'Skipping invalid URL: "{url}"')
            elif url in urls:
                logging.warning(f'Skipping duplicate URL: "{url}"')
            else:
                urls.append(url)
    return urls

def write_file(content, folder: str, filename: str, is_json=False) -> None:
    """
    Writes an Object to a file system.
    """
    logging.info(f'Saving file {filename} to folder {folder}...')
    output_text = None

    if is_json:
        output_text = json.dumps(content, indent=4)
    elif isinstance(content, str):
        output_text = content
    elif isinstance(content, list):
        output_text = '\n'.join(content)
    else:
        logging.warn(f'Content type is not recognized: {type(content)}!')
        output_text = content

    with open(f'{folder}/{filename}', 'w', encoding='utf-8') as f:
        f.write(output_text)

urls = loadUrls()
if len(urls) < 1:
    logging.error('No URLs found :(')
    sys.exit(1)
else:
    logging.info(f'{len(urls)} unique URLs found')

write_file(urls, BACKUP_FOLDER, f'{EXEC_TIME}-input.txt')

success = []
failures = []
counter = 0
with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
    total_urls = len(urls)
    for url in urls:
        counter += 1
        logging.info(f'Working on {counter} of {total_urls}: {url}')
        try:
            ydl.download([url])
            success.append(url)
        except:
            logging.error(f"An exception occurred with url '{url}'")
            failures.append(url)

write_file(success, BACKUP_FOLDER, f'{EXEC_TIME}-success.txt')
write_file(failures, BACKUP_FOLDER, f'{EXEC_TIME}-failures.txt')

logging.info(f'Success {len(success)}')
logging.info(f'Failures {len(failures)}')
logging.info(f'Total {counter}')
