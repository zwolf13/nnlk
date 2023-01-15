#!/usr/bin/env python
# coding: utf-8

import os
from pathlib import Path
import json
import logging
import logging.config
import configparser

# TODO Create a settings file? - https://stackoverflow.com/questions/13034496/using-global-variables-between-files
PATH = Path(__file__)
CURRENT_DIRECTORY = f'{PATH.parent}'
NNLK_CONFIG = os.path.join(PATH.parent.parent, 'nnlk.ini')
NNLK_LOG = os.path.join(PATH.parent.parent, 'logs', 'nnlk.log')
LOG_CONFIG = os.path.join(CURRENT_DIRECTORY, 'logger.ini')

logging.config.fileConfig(LOG_CONFIG, defaults={
                          'NNLK_LOG': NNLK_LOG.replace('\\', '/')})
LOG = logging.getLogger('UTILS')


def get_logger(name) -> logging.Logger:
    return logging.getLogger(name)


def load_config(file=NNLK_CONFIG, section='default'):
    section_config = {}
    config = configparser.ConfigParser()
    config.read(file)

    if section not in config.sections():
        LOG.error(f'No section "{section}" found in "{file}" :(')
    else:
        section_config = config[section]

    return section_config


def write_file(content, folder: str, filename: str, is_json=False) -> None:
    """Writes an Object to a file system."""
    LOG.info(f'Saving file: {filename}')
    output_text = None

    if is_json or isinstance(content, dict):
        output_text = json.dumps(content, indent=4)
    elif isinstance(content, str):
        output_text = content
    elif isinstance(content, list):
        output_text = '\n'.join(content)
    else:
        LOG.warning(f'Content type is not recognized: {type(content)}!')
        output_text = content

    with open(f'{folder}/{filename}', 'w', encoding='utf-8') as f:
        f.write(output_text)
