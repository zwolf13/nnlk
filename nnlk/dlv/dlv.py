#!/usr/bin/env python
# coding: utf-8

import sys
import getopt
import logging
import logging.config
import validators
import json
from datetime import datetime
from youtube_dl import YoutubeDL
import nnlk.commons.utils as utils
from nnlk.commons.constants import UNDERSCORE_DATE
import nnlk.dlv.finder as finder

# TODO
#  - Add a way to get the status: (different script?)
#      - Is running, cat log, entries in input urls.txt, number of failures, disk check (initial, current and final)

LOG = utils.get_logger('DLV')

# Script variables
EXEC_TIME = datetime.now().strftime(UNDERSCORE_DATE)
INPUT_URLS_FILE = 'urls.txt'
SUCCESS = []
FAILURES = []
COUNTER = 0

# Config variables
VERSION = None
HOST = None
BACKUP_FOLDER = None
OUTPUT_FOLDER = None
COOKIE = None
TEMPLATE = None


def main(argv: list[str]) -> None:
    """Entry point for DLV command-line"""
    _init()
    LOG.info(f'= NEW DOWNLOAD ===================================')
    urls = _handle_argv(argv)
    if not urls:
        urls = load_urls()
    # TODO - Read initial state of archive.txt
    download(urls)
    # TODO
    #  - Check the updated archive.txt file to determine the new entries (extractor/id)
    #  - Find the new files based of the new archive entries
    # verify_downloads()

    print_summary()
    LOG.info(f'==================================================')


def download(urls: list[str]) -> None:
    total_urls = len(urls)
    if total_urls < 1:
        msg = 'No URLs found :('
        LOG.error(msg)
        raise Exception(msg)
    else:
        utils.write_file(urls, BACKUP_FOLDER, f'{EXEC_TIME}-input.txt')

    global COUNTER
    global SUCCESS
    global FAILURES
    with YoutubeDL(_get_ytdl_opts()) as ydl:
        for url in urls:
            COUNTER += 1
            LOG.info(f"Working on {COUNTER} of {total_urls}: '{url}'")
            try:
                # TODO Refactor this to:
                #  1. Download metadata
                #  2. Determine extractor-specific parameters
                #  3. Check estimated video size vs disk space (add disk space check)
                #  4. Download video
                LOG.debug(f"downloading '{url}'...")
                ydl.download([url])
            except Exception as e:
                LOG.error(f'An exception occurred with url "{url}": "{e}"')
                FAILURES.append(url)
            else:
                LOG.info(f"Done: '{url}'")
                SUCCESS.append(url)

    utils.write_file(SUCCESS, BACKUP_FOLDER, f'{EXEC_TIME}-success.txt')
    utils.write_file(FAILURES, BACKUP_FOLDER, f'{EXEC_TIME}-failures.txt')


def verify_downloads() -> None:
    # TODO
    #  - Check for: .part .tmp *temp.* missing files missing suffix
    #  - Find same size files

    # Currently NNLK suffixes include:
    # .m4a          AUDIO
    # .mp3          AUDIO
    # .wav          AUDIO
    # .jpeg         IMAGE
    # .jpg          IMAGE
    # .gif          IMAGE
    # .png          IMAGE
    # .webp         IMAGE
    # .JPG          IMAGE
    # .mp4          VIDEO
    # .PNG          IMAGE
    # .db           SYSTEM
    # .wmv          VIDEO
    # .webm         VIDEO
    # .dtrashinfo   SYSTEM
    # .swf          VIDEO
    # .psd
    # .cpd
    # .xspf
    # .m3u          PLAYLIST
    # .mkv          VIDEO
    # .mov          VIDEO
    # .avi          VIDEO
    # .json         TEXT
    # .flv          VIDEO
    # .asx
    # .3gpp2
    # .mpg          VIDEO
    # .MOV          VIDEO
    # .txt          TEXT
    # .m4v
    # .ram
    # .asf
    # .ts           VIDEO
    # .image        IMAGE
    # .VOB
    # .3gp          VIDEO
    # .part         ???
    # .srt          TEXT

    # Getting all downloaded files
    finder._init()
    results = finder.search()

    suffixes = []
    sizes = []
    VALID_SUFFIXES = []
    INVALID_SUFFIXES = ['.part', '.db']
    same_size_files = []
    for result in results:
        suffix = result.get('suffix')
        size = result.get('size')

        if suffix not in suffixes:
            suffixes.append(suffix)
            print(suffix)

        if suffix in INVALID_SUFFIXES:
            print("")

        if size not in sizes:
            sizes.append(size)
        else:
            # print(result.get('name'))
            same_size_files.append(result.get('name'))


def print_usage() -> None:
    print(f'DLV version {VERSION}')
    print('Usage: dlv.py [OPTIONS] [URLs...]')
    print('\n')
    print('Options:')
    print('  --version                          Print program version and exit')
    print('  -h, --help                         Print this help text and exit')
    print('  -v, --verbose                      Print debugging information')
    print('  -i, --input-file FILE_PATH         Override default input file to FILE_PATH')
    print('  -o, --output-folder FOLDER_PATH    Override default output folder to FOLDER_PATH')
    print('  -c, --cookie FILE_PATH             Set the cookie file to use')


def print_version() -> None:
    print(VERSION)


def _init() -> None:
    """Initializes default config"""
    global VERSION
    global HOST
    global BACKUP_FOLDER
    global OUTPUT_FOLDER
    config = utils.load_config()
    VERSION = config.get('version')
    HOST = config.get('host')
    BACKUP_FOLDER = config.get('backup_folder')
    OUTPUT_FOLDER = config.get('output_folder')


def _handle_argv(argv: list[str]) -> list[str]:
    """Handles input parameters to override default config.
    If URLs where typed, they will be validated and a list of unique entries will be returned."""

    try:
        opts, args = getopt.getopt(
            argv, 'hvi:o:c:t:', ['help', 'version', 'verbose', 'input-file=', 'output-folder=', 'cookie=', 'template='])
    except getopt.GetoptError:
        LOG.error('Invalid parameters! :(')
        print_usage()
        sys.exit(1)

    # TODO
    #  - Add download metadata only option
    #  - Add force download option
    #  - Add a way to register externally downloaded videos (like using dwhelper)

    # Overloads default config
    global INPUT_URLS_FILE
    global OUTPUT_FOLDER
    global COOKIE
    global TEMPLATE
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print_usage()
            sys.exit(0)
        elif opt in ['--version']:
            print_version()
            sys.exit(0)
        elif opt in ['-v', '--verbose']:
            LOG.info('Setting Log Level to DEBUG')
            LOG.setLevel(logging.DEBUG)
            for handler in LOG.handlers:
                handler.setLevel(logging.DEBUG)
        elif opt in ['-i', '--input-file']:
            LOG.info(f'Overriding Input File: "{arg}"')
            INPUT_URLS_FILE = arg
        elif opt in ['-o', '--output-folder']:
            LOG.info(f'Overriding Output Folder: "{arg}"')
            OUTPUT_FOLDER = arg
        elif opt in ['-c', '--cookie']:
            LOG.info(f'Using cookie file: "{arg}"')
            COOKIE = arg
        elif opt in ['-t', '--template']:
            LOG.info(f'Using custom template: "{arg}"')
            TEMPLATE = arg
        else:
            LOG.warn(f'Ignoring unknown parameter: "{opt}"="{arg}"')

    urls = []
    if args and len(args) > 0:
        for url in args:
            _append_url(urls, url)

    return urls


def _append_url(urls: list, url: str) -> None:
    """Adds the new URL to given list if it is valid and it wasn't previously added to the list"""
    if not validators.url(url):
        LOG.warning(f'Skipping invalid URL: "{url}"')
    elif url in urls:
        LOG.warning(f'Skipping duplicate URL: "{url}"')
    else:
        LOG.debug(f'Appending "{url}"')
        urls.append(url)


def load_urls() -> list[str]:
    """Loads a list of URLs contained in urls.txt file."""
    LOG.info('Loading URLs')
    urls = []

    with open(INPUT_URLS_FILE) as urls_file:
        for line in urls_file:
            _append_url(urls, line.strip())

    return urls


def _get_ytdl_opts(extractor=None) -> dict:
    LOG.debug('Getting YouTubeDL options')
    opts = None
    with open('opts.json') as file:
        opts = json.load(file)

    # Dynamic opts
    global TEMPLATE
    opts['download_archive'] = f'{HOST}-archive.txt'
    opts['outtmpl'] = f'{OUTPUT_FOLDER}/%(extractor)s/%(title)s - %(id)s.%(ext)s' if TEMPLATE is None else f'{OUTPUT_FOLDER}/{TEMPLATE}'

    # TODO Get cookies from centralized location
    if COOKIE:
        LOG.debug(f'Adding cookie file to YTDL-OPTS: {COOKIE}')
        opts['cookiefile'] = COOKIE

    # TODO - Adding extractor-specific opts?
    if extractor is not None:
        LOG.warning(
            f'Pending implementation: Adding extractor-specific opts for "{extractor}"')

    return opts


def print_summary() -> None:
    global VERSION
    global BACKUP_FOLDER
    global OUTPUT_FOLDER
    global SUCCESS
    global FAILURES
    global COUNTER

    LOG.info(f'- SUMMARY ----------------------------------------')
    LOG.info(f'DLV VERSION    {VERSION}')
    LOG.info(f'BACKUP_FOLDER  {BACKUP_FOLDER}')
    LOG.info(f'OUTPUT_FOLDER  {OUTPUT_FOLDER}')
    LOG.info(f'SUCCESS        {len(SUCCESS)}')
    LOG.info(f'FAILURES       {len(FAILURES)}')
    LOG.info(f'TOTAL          {COUNTER}')


if __name__ == "__main__":
    main(sys.argv[1:])
