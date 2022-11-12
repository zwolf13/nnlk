#!/usr/bin/env python
# coding: utf-8

import sys
import getopt
from pathlib import Path
import re
import logging
import logging.config
from datetime import datetime
import nnlk.commons.utils as utils

LOG = utils.get_logger('FINDER')

# Script variables
QUERY = None
# TODO Create a settings file?
EXEC_TIME = datetime.now().strftime('%Y.%m.%d_%H.%M.%S')

# Config variables
HOST = None
SEARCH_PATH = None


def main(argv: list[str]) -> None:
    """Entry point for FINDER command-line"""
    _init()
    _handle_argv(argv)
    results = search(QUERY)

    if len(results) < 1:
        LOG.info(f'No results found for: "{QUERY}" :(')
    else:
        print_results(results)


def _init() -> None:
    """Initializes default script config"""
    global HOST
    global SEARCH_PATH
    config = utils.load_config()
    HOST = config.get('host')
    SEARCH_PATH = config.get('output_folder')


def _handle_argv(argv: list[str]) -> None:
    try:
        opts, args = getopt.getopt(argv, 'hv', ['help', 'verbose'])
    except getopt.GetoptError:
        LOG.error('Invalid parameters! :(')
        print_usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print_usage()
            sys.exit(0)
        elif opt in ['-v', '--verbose']:
            LOG.info('Setting Log Level to DEBUG')
            LOG.setLevel(logging.DEBUG)
            for handler in LOG.handlers:
                handler.setLevel(logging.DEBUG)
        else:
            LOG.warn(f'Ignoring unknown parameter: "{opt}"="{arg}"')

    global QUERY
    if not args:
        LOG.error('Query parameter missing! :(')
        print_usage()
        sys.exit(1)
    elif len(args) > 1:
        LOG.error('Only one query parameter is allowed! :(')
        print_usage()
        sys.exit(1)
    else:
        QUERY = args[0]


def print_usage() -> None:
    print('Usage: finder.py [OPTIONS] <QUERY>')
    print('\n')
    print('Options:')
    print('  -h, --help                         Print this help text and exit')
    print('  -v, --verbose                      Print debugging information')


def search(query = '.') -> list[dict[str, any]]:
    # TODO - Add the capability of override default search directory (SEARCH_PATH)
    global SEARCH_PATH
    pattern = None
    results = []
    LOG.debug(f'Searching for "{query}" in "{SEARCH_PATH}"')

    try:
        pattern = re.compile(query, re.IGNORECASE)
    except Exception as e:
        LOG.error(f'Invalid query "{query}": "{e}" :(')
    else:
        for path in Path(SEARCH_PATH).rglob('*'):
            if path.is_file() and re.search(pattern, path.name):
                results.append(build_result(path))

    return results


def build_result(path: Path) -> dict[str, any]:
    stat = path.stat()
    return {
        'name': path.name,
        'suffix': path.suffix,
        'path': str(path.parent),
        'size': stat.st_size,
        'created': datetime.fromtimestamp(stat.st_ctime).strftime('%m/%d/%Y %H:%M:%S')
    }


def print_results(results: list) -> None:
    # TODO
    #  - Documentation
    #  - Fix UTF-8 print in Widows:
    #      sys.stdout.reconfigure(encoding='utf-8')
    #      result.get('name').encode('utf-8')
    #      Run CHCP 65001 in cmd
    for result in results:
        print(result.get('name'))


if __name__ == "__main__":
    main(sys.argv[1:])
