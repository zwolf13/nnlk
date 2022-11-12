#!/usr/bin/env python
# coding: utf-8

import os
from pathlib import Path
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
