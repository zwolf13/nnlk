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
#	'cookiefile': '',
  'outtmpl': 'downloads/%(extractor)s/%(title)s - %(id)s.%(ext)s',
	 'download_archive': 'dev-archive.txt'
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
  ydl.download(['https://www.tiktok.com/t/ZTRUruv4j/?k=1'])
