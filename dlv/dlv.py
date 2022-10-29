# coding: utf-8

import sys
import getopt
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
VERSION = '2022.10.27-1'
EXEC_TIME = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
INPUT_URLS_FILE = 'urls.txt'
SUCCESS = []
FAILURES = []
COUNTER = 0

# Config variables
HOST = None
BACKUP_FOLDER = None
OUTPUT_FOLDER = None


def print_usage() -> None:
    print('dlv.py [-i <input_file>] [-o <output_file>]')


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


def get_ytdl_opts(extractor=None) -> dict:
    log.info('Getting YouTubeDL options')

    # TODO - Config number of retries
    log.debug('Loading default opts')
    opts = None
    with open('default-opts.json') as file:
        opts = json.load(file)

    log.debug('Adding dynamic opts')
    opts['outtmpl'] = f'{OUTPUT_FOLDER}/%(extractor)s/%(title)s - %(id)s.%(ext)s'
    opts['download_archive'] = f'{HOST}-archive.txt'

    # TODO - Adding extractor-specific opts?
    if extractor is not None:
        log.warning(
            f'Pending implementation: Adding extractor-specific opts for "{extractor}"')

    # Make cookiefile dynamic and an optional parameter
    # get cookies from centralized location
    # 'cookiefile': 'cookies/youtube.txt'

    log.warning('Pending implementation: Override default opts')

    return opts


def write_file(content, folder: str, filename: str, is_json=False) -> None:
    """Writes an Object to a file system."""
    log.info(f'Saving file: {filename}')
    output_text = None

    if is_json or isinstance(content, dict):
        output_text = json.dumps(content, indent=4)
    elif isinstance(content, str):
        output_text = content
    elif isinstance(content, list):
        output_text = '\n'.join(content)
    else:
        log.warning(f'Content type is not recognized: {type(content)}!')
        output_text = content

    with open(f'{folder}/{filename}', 'w', encoding='utf-8') as f:
        f.write(output_text)


def print_summary() -> None:
    log.info(f'------------------------------')
    log.info(f'DLV VERSION    {VERSION}')
    log.info(f'OUTPUT_FOLDER  {OUTPUT_FOLDER}')
    log.info(f'SUCCESS        {len(SUCCESS)}')
    log.info(f'FAILURES       {len(FAILURES)}')
    log.info(f'TOTAL          {COUNTER}')
    log.info(f'------------------------------')


# TODO
# def main():
#     print('all starts here')
#
# if __name__ == "__main__":
#    main(sys.argv[1:])


# TODO Check for an input list before loading URLs from file
# TODO Fix long-name opts
# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
urls = []
try:
    opts, args = getopt.getopt(sys.argv[1:], 'hi:o:u:', [
                               'input-file=', 'output-file=', 'url='])
except getopt.GetoptError:
    log.error('Invalid parameters! :(')
    print_usage()
    sys.exit(1)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        print_usage()
        sys.exit(0)
    elif opt in ('-i', '--input-file'):
        inputfile = arg
    elif opt in ('-o', '--output-file'):
        outputfile = arg
    elif opt in ('-u', '--url'):
        if not validators.url(arg):
            log.warning(f'Skipping invalid URL: "{arg}"')
        else:
            urls.append(arg)


init()
if len(urls) < 1:
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
            #  3. Check estimated video size vs disk space
            #  4. Download video
            ydl.download([url])
            SUCCESS.append(url)
        except:
            log.error(f"An exception occurred with url '{url}'")
            FAILURES.append(url)

write_file(SUCCESS, BACKUP_FOLDER, f'{EXEC_TIME}-success.txt')
write_file(FAILURES, BACKUP_FOLDER, f'{EXEC_TIME}-failures.txt')
print_summary()
