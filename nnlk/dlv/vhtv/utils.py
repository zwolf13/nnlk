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


def get_times(local_timestamp=None, video_timestamp=None, available_timestamp=None, url_timestamp=None):
    if not local_timestamp and not video_timestamp and not available_timestamp and not url_timestamp:
        local_timestamp = int(time.time())
    if local_timestamp is not None:
        video_timestamp = local_timestamp + 43200
        available_timestamp = video_timestamp - 86400
        url_timestamp = available_timestamp - 25200
    elif video_timestamp is not None:
        available_timestamp = video_timestamp - 86400
        url_timestamp = available_timestamp - 25200
        local_timestamp = video_timestamp - 43200
    elif available_timestamp is not None:
        url_timestamp = available_timestamp - 25200
        video_timestamp = available_timestamp + 86400
        local_timestamp = video_timestamp - 43200
    elif url_timestamp is not None:
        available_timestamp = url_timestamp + 25200
        video_timestamp = available_timestamp + 86400
        local_timestamp = video_timestamp - 43200
    else:
        raise Exception('Something went wrong ;(')
    local_date = datetime.fromtimestamp(local_timestamp).strftime(DATE_FMT)
    video_date = datetime.fromtimestamp(video_timestamp).strftime(DATE_FMT)
    available_date = datetime.fromtimestamp(available_timestamp).strftime(DATE_FMT)
    url_date = datetime.fromtimestamp(url_timestamp).strftime(DATE_FMT)

    return {
        'local_timestamp': local_timestamp,
        'video_timestamp': video_timestamp,
        'available_timestamp': available_timestamp,
        'url_timestamp': url_timestamp,
        'local_date': local_date,
        'video_date': video_date,
        'available_date': available_date,
        'url_date': url_date,
    }


def print_times(times: dict):
    print(f'local:      {times.get("local_timestamp")}  =>  {times.get("local_date")}')
    print(f'video:      {times.get("video_timestamp")}  =>  {times.get("video_date")}')
    print(f'available:  {times.get("available_timestamp")}  =>  {times.get("available_date")}')
    print(f'url:        {times.get("url_timestamp")}  =>  {times.get("url_date")}')


def date_to_ts(date):
    return int(time.mktime(datetime.strptime(date, DATE_FMT).timetuple()))
