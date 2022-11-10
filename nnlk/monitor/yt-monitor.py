import re
import requests
import json
from jsonpath_ng import parse
from datetime import datetime

DEBUG = False
OUTPUT_FOLDER = 'C:/Users/Mauricio/Downloads/tmp/youtube-monitor'
ARCHIVED_VIDEO_IDS = 'C:/Users/Mauricio/Downloads/tmp/youtube-monitor/archived-ids.txt'

def write_file(object, filename, is_json = False):
    print(f'Saving file: {filename}...')
    output_text = json.dumps(object, indent = 4) if is_json else object
    with open(f'{OUTPUT_FOLDER}/{filename}', 'w', encoding='utf-8') as f:
        f.write(output_text)

def download_html(url):
    print(f'Downloading HTML from: {url}...')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    }
    html_page = requests.get(url, headers = headers)
    if html_page.status_code == 200:
        content = html_page.text
        if DEBUG:
            write_file(content, 'youtube.html')
        return content
    else:
        print("Couldn't download HTML page :(")
        return ''

def update_archived_ids(new_ids):
    print('Updating archived IDs...')
    output_lines = ["{}\n".format(new_id) for new_id in new_ids]
    open(ARCHIVED_VIDEO_IDS, 'a').writelines(output_lines)

my_html = download_html('https://www.youtube.com/results?search_query=snoring&sp=CAI%253D')
match = re.search(r'var ytInitialData = ([^;]*);', my_html, re.M)

if not match:
    print("Couldn't find ytInitialData in HTML :(")
    exit(0)

initial_data = json.loads(match.group(1))

if DEBUG:
    write_file(initial_data, 'initial-data.json', is_json = True)

yt_results = [match.value for match in parse('$..videoRenderer').find(initial_data)]

if DEBUG:
    write_file(yt_results, 'yt-results.json', is_json = True)

results = []
for yt_result in yt_results:
    video_id = yt_result.get('videoId')
    channel_id = yt_result.get('ownerText', {}).get('runs', [{}])[0].get('navigationEndpoint', {}).get('browseEndpoint', {}).get('browseId')
    summary_result = {
        'video_id': video_id,
        'video_url': f'https://youtu.be/{video_id}',
        'thumbnail': yt_result.get('thumbnail', {}).get('thumbnails', [{}])[0],
        'title': yt_result.get('title', {}).get('runs', [{}])[0].get('text'),
        'video_length': yt_result.get('lengthText', {}).get('simpleText'),
        'uploader': yt_result.get('ownerText', {}).get('runs', [{}])[0].get('text'),
        'channel_id': channel_id,
        'channel_url': f'https://www.youtube.com/channel/{channel_id}'
    }
    results.append(summary_result)

archived_video_ids = open(ARCHIVED_VIDEO_IDS).read().splitlines()
results_2_video_ids = map(lambda result: result.get('video_id'), results)
video_ids = list(results_2_video_ids)
new_video_ids = [video_id for video_id in video_ids if video_id not in archived_video_ids]
new_video_count = len(new_video_ids)
estimated_results = int(initial_data.get('estimatedResults'))

print(f'Estimated results: {estimated_results:,}')
if new_video_count > 0:
    print(f'{new_video_count} new results found!')
    update_archived_ids(new_video_ids)
    new_results = [result for result in results if result.get('video_id') in new_video_ids]
    summary = {
        'estimated_results': estimated_results,
        'results': new_results
    }
    now = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
    write_file(summary, f'summary-{now}.json', is_json = True)
else:
    print(f'No new results found :(')
