# coding: utf-8

import youtube_dl

ydl_opts = {
    'nocheckcertificate': True,
    'format': 'best[ext=mp4]/best',
    'nooverwrites': True,
    'noprogress': True,
    'restrictfilenames': True,
    'writeinfojson': True,
    'writethumbnail': True,
    'writesubtitles': True,
    'cookiefile': 'cookies/youtube.txt',
    'outtmpl': 'downloads/%(extractor)s/%(title)s - %(id)s.%(ext)s',
    'download_archive': 'dev-archive.txt'
}

urls = []
with open('urls.txt') as f:
    urls = f.read().splitlines()

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    for url in urls:
        print(f'Working on: {url}')
        try:
            ydl.download([url])
        except:
            print(f"An exception occurred with url '{url}'") 
