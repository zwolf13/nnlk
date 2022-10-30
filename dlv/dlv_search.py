#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import re
import json
import logging
import logging.config
from .utils import load_config

logging.config.fileConfig('logger.ini')
LOG = logging.getLogger('DLV_SEARCH')


def dlv_search(query: str = None, type: str = None):
    status = 'OK'
    pattern = None
    results = []
    error = None
    config = load_config()
    search_path = config.get('output_folder')

    # TODO validate search_path

    LOG.info(f'Searching for "{query}" in "{search_path}"')
    try:
        pattern = re.compile(query, re.IGNORECASE)
    except Exception as e:
        LOG.error(f'An exception occurred with query "{query}": "{e}"')
        status = 'ERROR'
        error = str(e)

    for path in Path(search_path).rglob('*'):
        if path.is_file() and re.search(pattern, path.name):
            # TODO Add more properties to file
            file = {
                'name': path.name
            }
            results.append(file)

    response = {
        'status': status,
        'error': error,
        'entries': len(results),
        'results': results
    }

    return json.dumps(response, indent=4)
