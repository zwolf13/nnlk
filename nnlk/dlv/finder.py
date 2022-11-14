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
from nnlk.commons.constants import UNDERSCORE_DATE

LOG = utils.get_logger('FINDER')

# Script variables
EXEC_TIME = datetime.now().strftime(UNDERSCORE_DATE)
QUERY = None
SEARCH_PATH = None

# Config variables
HOST = None
DEFAULT_QUERY = '.'
DEFAULT_SEARCH_PATH = None


def main(argv: list[str]) -> None:
    """Entry point for FINDER command-line"""
    global QUERY
    global SEARCH_PATH
    _init()
    _handle_argv(argv)
    results = search(QUERY, SEARCH_PATH)

    if len(results) < 1:
        LOG.info(f'No results found for: "{QUERY}" :(')
    else:
        print_results(results)


def _init() -> None:
    """Initializes default script config"""
    global HOST
    global DEFAULT_SEARCH_PATH
    config = utils.load_config()
    HOST = config.get('host')
    DEFAULT_SEARCH_PATH = config.get('output_folder')


def _handle_argv(argv: list[str]) -> None:
    global SEARCH_PATH
    global QUERY

    try:
        # TODO - Add output file to save results into
        opts, args = getopt.getopt(
            argv, 'hvp:', ['help', 'verbose', 'search-path='])
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
        elif opt in ['-p', '--search-path']:
            SEARCH_PATH = arg
        else:
            LOG.warn(f'Ignoring unknown parameter: "{opt}"="{arg}"')

    if len(args) > 1:
        LOG.error('Only one query parameter is allowed! :(')
        print_usage()
        sys.exit(1)
    elif len(args) == 1:
        QUERY = args[0]


def print_usage() -> None:
    print('Usage: finder.py [OPTIONS] <QUERY>')
    print('\n')
    print('Options:')
    print('  -h, --help                         Print this help text and exit')
    print('  -v, --verbose                      Print debugging information')


def search(query=None, search_path=None) -> list[dict[str, any]]:
    if not query:
        query = DEFAULT_QUERY
    if not search_path:
        search_path = DEFAULT_SEARCH_PATH

    try:
        pattern = re.compile(query, re.IGNORECASE)
        pure_path = Path(search_path)
        if not pure_path.exists() or not pure_path.is_dir():
            raise Exception()
    except re.error as e:
        LOG.error(f'Invalid query "{query}": "{e}" :(')
    except Exception:
        LOG.error(f'Invalid search path: "{str(pure_path)}"')
    else:
        return [build_result(path) for path in pure_path.rglob('*') if path.is_file() and re.search(pattern, path.name)]


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
