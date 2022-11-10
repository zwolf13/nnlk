#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request
# https://docs.python.org/3/reference/import.html?highlight=relative%20imports#package-relative-imports
from nnlk.dlv.dlv import main
import nnlk.dlv.finder as finder

# https://flask.palletsprojects.com/
app = Flask(__name__)

# USAGE: python -m flask --app dlv-ws [--debug] run

# TODO
#  - Connect to dlv.py
#  - Start/Stop downloader, queue empty => wait for elements
#  - Maintain a queue of URLs
#     - Add URL to queue
#  - Retry last failures


@app.route('/dlv/version', methods=['GET'])
def status() -> dict:
    return {'version': 'TODO - Return version from .ini file'}


@app.route('/dlv/download', methods=['GET'])
def test() -> dict[str, str]:
    url = request.args.get('url')
    # TODO Run main asynchonously
    main([url])
    return {'status': 'OK', 'url': f'{url}'}


@app.route('/dlv/search', methods=['GET'])
def search() -> dict[str, any]:
    # TODO status, error and entries should be set here
    return finder.search(request.args.get('query'))
