import json
import urllib.request
from urllib.parse import urlparse
from jsonpath_ng import parse
from datetime import datetime
import os
import lxml.html
from lxml.html import builder
import lxml.etree
from string import Template

def create_folder(folder_path):
    print('Creating new folder: {}...'.format(folder_path))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def write_json(results_json, json_path):
    print('Writing JSON: {}...'.format(json_path))
    formatted = json.dumps(results_json, indent=2, sort_keys=True)
    output_file = open(json_path, "w")
    output_file.write(formatted)
    output_file.close()

def fetch_results(today_path):
    print('Fetching results from YouTube...')
    url = 'https://www.youtube.com/youtubei/v1/search?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false'
    data_string = open('data.json').read()
    data_bytes = data_string.encode('utf-8')
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'Origin': 'https://www.youtube.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
        'Content-Length': len(data_bytes),
        }
    request = urllib.request.Request(url, method='POST', headers=headers, data=data_bytes)
    response = urllib.request.urlopen(request)
    content_bytes = response.read()
    content_string = content_bytes.decode('utf8')
    results_json = json.loads(content_string)
    write_json(results_json, "{}/full-response.json".format(today_path))
    return results_json

def process_response(json_response, today_path):
    print('Procesing response...')
    todays_results = []
    for match in parse('$..videoRenderer').find(json_response):
        video_renderer = match.value
        id = video_renderer['videoId']
        channel_id = video_renderer['longBylineText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']
        canonical_base_url = video_renderer['longBylineText']['runs'][0]['navigationEndpoint']['browseEndpoint']['canonicalBaseUrl']
        all_thumbnails = video_renderer['thumbnail']['thumbnails']
        thumbnail = all_thumbnails[len(all_thumbnails) - 1]['url']
        details = {
            'channel_id': channel_id,
            'channel_url': "https://www.youtube.com{}".format(canonical_base_url),
            'duration': video_renderer['lengthText']['simpleText'],
            'id': id,
            'thumbnail': thumbnail,
            'title': video_renderer['title']['runs'][0]['text'],
            'uploader': video_renderer['longBylineText']['runs'][0]['text'],
            "webpage_url": "https://www.youtube.com/watch?v={}".format(id),
        }
        todays_results.append(details)
    write_json(todays_results, "{}/results.json".format(today_path))
    return todays_results

def find_new_ids(today_results, today_path, now_string):
    print('Identifying new IDs...')
    archived_ids = open('youtube/archived-ids.txt').read().splitlines()
    results2ids_map = map(lambda today_result: today_result.get('id'), today_results)
    today_ids = list(results2ids_map)
    new_ids = [today_id for today_id in today_ids if today_id not in archived_ids]
    new_ids_length = len(new_ids)

    if new_ids_length > 0:
        print('Found {} new IDs'.format(new_ids_length))
        write_json(new_ids, "{}/new-ids.json".format(today_path))
        fetch_metadata(new_ids, today_results, today_path)
        update_archived_ids(new_ids)
        create_summary(now_string, new_ids, today_results)
    else:
        print('No new IDs found :(')

def fetch_metadata(new_ids, today_results, today_path):
    print('Fetching new metadata...')
    thumbnails = [{'id': today_result.get('id'), 'url': today_result.get('thumbnail')}
        for today_result in today_results if today_result.get('id') in new_ids]
    for thumbnail in thumbnails: 
        url = thumbnail.get('url')
        id = thumbnail.get('id')
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]
        image_path = "{}/{}{}".format(today_path, id, ext)
        try:
            urllib.request.urlretrieve(url, image_path)
        except urllib.error.HTTPError:
            print('Error while fetching image: {}'.format(url))

def update_archived_ids(new_ids):
    print('Updating archived IDs...')
    output_lines = ["{}\n".format(new_id) for new_id in new_ids]
    open('youtube/archived-ids.txt', 'a').writelines(output_lines)

def create_summary(now_string, new_ids, today_results):
    print('Creating Summary file...')
    title = "New YouTube Results - {}".format(now_string)
    template_string = open('youtube/element-template.html').read()
    style = open('youtube/summary.css').read()

    string_elements = []
    for new_id in new_ids:
        details = next(result for result in today_results if result.get('id') == new_id)
        template = Template(template_string)
        string_element = template.substitute(**details)
        string_elements.append(string_element)

    html_elements = lxml.html.fromstring(''.join(string_elements))
    html = builder.HTML(
        builder.HEAD(
            builder.TITLE(title),
            builder.STYLE(style)
        ),
        builder.BODY(
            builder.H2(title),
            html_elements,
        )
    )
    html_string = lxml.html.tostring(html, pretty_print=True).decode('utf8')
    output_file = open('youtube/summary-{}.html'.format(now_string), "w")
    output_file.write(html_string)
    output_file.close()

now_string = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
today_path = 'youtube/{}'.format(now_string)
create_folder(today_path)
json_response = fetch_results(today_path)
today_results = process_response(json_response, today_path)
find_new_ids(today_results, today_path, now_string)

# Send email notification
