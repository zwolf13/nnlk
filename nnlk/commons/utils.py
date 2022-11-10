#!/usr/bin/env python
# coding: utf-8

import logging
import logging.config
import configparser

logging.config.fileConfig('logger.ini')
log = logging.getLogger('UTILS')

def load_config(file, section = 'default'):
    section_config = None
    config = configparser.ConfigParser()
    config.read(file)

    if section not in config.sections():
        log.error(f'No section "{section}" found in "{file}" :(')
        # TODO - Raise error
    else:
        section_config = config[section]
    
    return section_config
