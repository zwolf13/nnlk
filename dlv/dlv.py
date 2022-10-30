#!/usr/bin/env python
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


def main(argv: list[str]) -> None:
    _init()
    urls = _handle_argv(argv)
    if not urls:
        urls = load_urls()
    write_file(urls, BACKUP_FOLDER, f'{EXEC_TIME}-input.txt')
    download_files(urls)
    write_file(SUCCESS, BACKUP_FOLDER, f'{EXEC_TIME}-success.txt')
    write_file(FAILURES, BACKUP_FOLDER, f'{EXEC_TIME}-failures.txt')
    print_summary()


def download_files(urls: list[str]) -> None:
    total_urls = len(urls)
    if total_urls < 1:
        log.error('No URLs found :(')
        sys.exit(1)

    global COUNTER
    with YoutubeDL(_get_ytdl_opts()) as ydl:
        for url in urls:
            COUNTER += 1
            log.info(f"Working on {COUNTER} of {total_urls}: '{url}'")
            try:
                # TODO Refactor this to:
                #  1. Download metadata
                #  2. Determine extractor-specific parameters
                #  3. Check estimated video size vs disk space (add disk space check)
                #  4. Download video
                ydl.download([url])
                SUCCESS.append(url)
            except:
                log.error(f'An exception occurred with url "{url}"')
                FAILURES.append(url)


def print_usage() -> None:
    print('Usage: dlv.py [OPTIONS] [URLs...]')
    print('\n')
    print('Options:')
    print('  --version                          Print program version and exit')
    print('  -h, --help                         Print this help text and exit')
    print('  -v, --verbose                      Print debugging information')
    print('  -i, --input-file FILE_PATH         Override default input file to FILE_PATH')
    print('  -o, --output-folder FOLDER_PATH    Override default output folder to FOLDER_PATH')


def print_version() -> None:
    print(f'DLV v{VERSION}')


def _init() -> None:
    """Initializes default config"""
    global HOST
    global BACKUP_FOLDER
    global OUTPUT_FOLDER

    config = configparser.ConfigParser()
    config.read('dlv.ini')
    default = None

    if 'default' not in config.sections():
        log.error('No default config found :(')
        sys.exit(1)
    else:
        default = config['default']

    HOST = default.get('host')
    BACKUP_FOLDER = default.get('backup_folder')
    OUTPUT_FOLDER = default.get('output_folder')


def _handle_argv(argv: list[str]) -> list[str]:
    """Handles input parameters to override default config.
    If URLs where typed, they will be validated and a list of unique entries will be returned."""
    log.debug('Handling input arguments')

    try:
        opts, args = getopt.getopt(
            argv, 'hvi:o:', ['help', 'version', 'verbose', 'input-file=', 'output-folder='])
    except getopt.GetoptError:
        log.error('Invalid parameters! :(')
        print_usage()
        sys.exit(1)

    # Overloads default config
    global INPUT_URLS_FILE
    global OUTPUT_FOLDER
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print_usage()
            sys.exit(0)
        elif opt in ['--version']:
            print_version()
            sys.exit(0)
        if opt in ['-v', '--verbose']:
            log.info('Setting Log Level to DEBUG')
            log.setLevel(logging.DEBUG)
        elif opt in ['-i', '--input-file']:
            log.info(f'Overriding Input File: "{arg}"')
            INPUT_URLS_FILE = arg
        elif opt in ['-o', '--output-folder']:
            log.info(f'Overriding Output Folder: "{arg}"')
            OUTPUT_FOLDER = arg

    urls = []
    if args and len(args) > 0:
        for url in args:
            _append_url(urls, url)

    return urls


def _append_url(urls: list, url: str) -> None:
    """Adds the new URL to given list if it is valid and it wasn't previously added to the list"""
    if not validators.url(url):
        log.warning(f'Skipping invalid URL: "{url}"')
    elif url in urls:
        log.warning(f'Skipping duplicate URL: "{url}"')
    else:
        log.debug(f'Appending "{url}"')
        urls.append(url)


def load_urls() -> list[str]:
    """Loads a list of URLs contained in urls.txt file."""
    log.info('Loading URLs')
    urls = []

    with open(INPUT_URLS_FILE) as urls_file:
        for line in urls_file:
            _append_url(urls, line.strip())

    return urls


def _get_ytdl_opts(extractor=None) -> dict:
    log.debug('Getting YouTubeDL options')
    opts = None
    with open('opts.json') as file:
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
    log.info(f'--------------------------------------------------')
    log.info(f'DLV VERSION    {VERSION}')
    log.info(f'OUTPUT_FOLDER  {OUTPUT_FOLDER}')
    log.info(f'SUCCESS        {len(SUCCESS)}')
    log.info(f'FAILURES       {len(FAILURES)}')
    log.info(f'TOTAL          {COUNTER}')
    log.info(f'--------------------------------------------------')


if __name__ == "__main__":
    main(sys.argv[1:])
