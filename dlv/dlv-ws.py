#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from .dlv import load_urls  # TODO Why this is not connected?

# https://flask.palletsprojects.com/
app = Flask(__name__)

# TODO
#  - Connect to dlv.py
#  - Start/Stop downloader, queue empty => wait for elements
#  - Maintain a queue of URLs
#     - Add URL to queue


@app.get("/dlv/status")
def status():
    return {"status": "OK"}


@app.get("/dlv/test")
def test() -> list[str]:
    return load_urls()


@app.get("/dlv/search-logs")
def search() -> list[str]:
    return load_urls()
