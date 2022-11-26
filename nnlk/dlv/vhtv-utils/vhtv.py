import time
from datetime import datetime

"""
                VIDEO TIME              TIMESTAMP       URL
Current time:   11/26/2022 09:50 AM     1669456200
Video time:     11/26/2022 21:50 PM     1669499400
Available time: 11/25/2022 21:50 PM     1669413000      1669387800 => 11/25/2022 02:50 PM

VIDEO_TIME = CURRENT_TIME + 43200 (+12 HRS)
AVAILABLE  = VIDEO_TIME - 86400 (-24 HRS)
URL_TIME   = AVAILABLE - 25200 (-7 HRS)
"""

DATE_FMT = '%m/%d/%Y %H:%M:%S'


def get_times_1():
    current_time = int(time.time())
    video_time = current_time + 43200
    available_time = video_time - 86400
    url_time = available_time - 25200
    print(f'current_time: {current_time}')
    print(f'video_time: {video_time}')
    print(f'available_time: {available_time}')
    print(f'url_time: {url_time}')


def get_times(current_time=None):
    if not current_time:
        current_time = int(time.time())
    video_time = current_time + 43200
    available_time = video_time - 86400
    url_time = available_time - 25200
    print(
        f'current_time:    {current_time}  => {datetime.fromtimestamp(current_time).strftime("%m/%d/%Y %H:%M:%S")}')
    print(
        f'video_time:      {video_time}  => {datetime.fromtimestamp(video_time).strftime("%m/%d/%Y %H:%M:%S")}')
    print(
        f'available_time:  {available_time}  => {datetime.fromtimestamp(available_time).strftime("%m/%d/%Y %H:%M:%S")}')
    print(
        f'url_time:        {url_time}  => {datetime.fromtimestamp(url_time).strftime("%m/%d/%Y %H:%M:%S")}')


def get_times_by(current_time=None, video_time=None, available_time=None, url_time=None):
    if not current_time and not video_time and not available_time and not url_time:
        current_time = int(time.time())
    if current_time is not None:
        video_time = current_time + 43200
        available_time = video_time - 86400
        url_time = available_time - 25200
    elif video_time is not None:
        available_time = video_time - 86400
        url_time = available_time - 25200
        current_time = video_time - 43200
    elif available_time is not None:
        url_time = available_time - 25200
        video_time = available_time + 86400
        current_time = video_time - 43200
    elif url_time is not None:
        available_time = url_time + 25200
        video_time = available_time + 86400
        current_time = video_time - 43200
    else:
        raise Exception('Something went wrong ;(')
    current_date = datetime.fromtimestamp(current_time).strftime(DATE_FMT)
    video_date = datetime.fromtimestamp(video_time).strftime(DATE_FMT)
    available_date = datetime.fromtimestamp(available_time).strftime(DATE_FMT)
    url_date = datetime.fromtimestamp(url_time).strftime(DATE_FMT)
    print(f'current_time:    {current_time}  =>  {current_date}')
    print(f'video_time:      {video_time}  =>  {video_date}')
    print(f'available_time:  {available_time}  =>  {available_date}')
    print(f'url_time:        {url_time}  =>  {url_date}')
