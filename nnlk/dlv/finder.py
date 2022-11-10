#!/usr/bin/env python
# coding: utf-8

import sys
import getopt
from pathlib import Path
import re
import logging
import logging.config
from datetime import datetime
from nnlk.commons.utils import load_config

logging.config.fileConfig('logger.ini')
LOG = logging.getLogger('FINDER')

# Script constans
OK = 'OK'
ERROR = 'ERROR'

# Script variables
QUERY = None
EXEC_TIME = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")

# Config variables
HOST = None


def main(argv: list[str]) -> None:
    """Entry point for FINDER command-line"""
    _init()
    _handle_argv(argv)
    response = search(QUERY)

    if response.get('status') == ERROR:
        LOG.error(f'An error occured while searching for: "{QUERY}" :(')
        LOG.error(response.get('error'))
    elif response.get('entries', 0) < 1:
        LOG.info(f'No results found for: "{QUERY}" :(')
    else:
        for result in response.get('results'):
            print(result.get('name'))


def _init() -> None:
    """Initializes default config"""
    global HOST
    config = load_config('dlv.ini')
    HOST = config.get('host')


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


def search(query) -> dict[str, any]:
    status = OK
    pattern = None
    results = []
    error = None
    config = load_config('dlv.ini') # TODO move this to _init
    search_path = config.get('output_folder') # TODO move this to _init

    # TODO validate search_path

    LOG.debug(f'Searching for "{query}" in "{search_path}"')
    try:
        pattern = re.compile(query, re.IGNORECASE)
    except Exception as e:
        LOG.error(f'An exception occurred with query "{query}": "{e}"')
        status = ERROR
        error = str(e)

    for path in Path(search_path).rglob('*'):
        if path.is_file() and re.search(pattern, path.name):
            # TODO Add more properties to file
            file = {
                'name': path.name
            }
            results.append(file)
    # TODO return only results or error, other props should be set in dlv-ws
    return {
        'status': status,
        'error': error,
        'entries': len(results),
        'results': results
    }


if __name__ == "__main__":
    main(sys.argv[1:])
