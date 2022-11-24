#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request
from datetime import datetime
import threading
from nnlk.commons.constants import UNDERSCORE_DATE
import nnlk.commons.utils as utils
import nnlk.dlv.dlv as dlv
import nnlk.dlv.finder as finder

# https://flask.palletsprojects.com/
app = Flask(__name__)

# USAGE: python -m flask --app dlv-ws [--debug] run

# TODO
#  - Add swagger
#  - Start/Stop downloader, queue empty => wait for elements
#  - Maintain a queue of URLs
#     - Add URL to queue
#  - Retry last failures
#  - Get logs

LOG = utils.get_logger('DLV-WS')

# Script variables
EXEC_TIME = datetime.now().strftime(UNDERSCORE_DATE)

# Config variables
VERSION = None
HOST = None
BACKUP_FOLDER = None
OUTPUT_FOLDER = None
COOKIE = None


@app.before_first_request
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
    dlv._init()


@app.route('/dlv/version', methods=['GET'])
def get_version() -> dict[str, str]:
    return {'version': VERSION}


@app.route('/dlv/download', methods=['GET'])
def download() -> dict[str, str]:
    status = None
    message = None
    url = None

    try:
        url = request.args.get('url')
        my_thread = threading.Thread(target=dlv.download_files, args=([url],))
        my_thread.start()
    except Exception as e:
        LOG.error(f'An exception occurred with url "{url}": "{e}"')
        status = 'ERROR'
        message = str(e)
    else:
        status = 'OK'
        message = f'Started download: {url}'
    
    return {'status': status, 'message': message}


@app.route('/dlv/search', methods=['GET'])
def search() -> dict[str, any]:
    # TODO status, error and entries should be set here
    return finder.search(request.args.get('query'))
