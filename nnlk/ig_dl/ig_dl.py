import re
import requests
import json
import shutil
import sys
from datetime import datetime
from http.cookiejar import MozillaCookieJar

OUTPUT_FOLDER = 'C:/Users/Mauricio/dwhelper/Instagram'
DEBUG = False

def get_cookie_header():
    return 'csrftoken=aMSU26xkWCSMqYBqTKfmXU7oypTAX9Od; mid=YtVnLAAEAAGwNT-WIsVuz-ohGSs5; ig_did=C3D3162C-1019-4012-87A4-1DB6201F23B1; ig_nrcb=1; ds_user_id=3452129080; sessionid=3452129080%3AQviA2eUVAUMZVb%3A6%3AAYeSasN7kXGs7vH5bagdOH0meIA8fmxtd2QDi6BfpQ; shbid="19869\0543452129080\0541690037766:01f7f5dcefaafdfd5daa6762d10862587052a0172e2945abac88ea632e564a6f499cc72e"; shbts="1658501766\0543452129080\0541690037766:01f78113c0c6ec028d1de8b45213298b8638f1285aa4c0e874fc466d62dbf46e16b23d56"; datr=eWfVYnecei_NfGDgohf3_lJV; fbm_124024574287414=base_domain=.instagram.com; rur="NCG\0543452129080\0541690292972:01f7e11a6e3e93e3f0b584346b6301b560be1336eb4210b9000c1ea9ee5448db1035fee3"; fbsr_124024574287414=o3JB0jp4K1zthT-ao5MJWqUnouwGZZmqC2W_w6jTnq4.eyJ1c2VyX2lkIjoiNjAyNjE5Nzg2IiwiY29kZSI6IkFRQTFxcVpWZkxwUHVpRG9BNEE4Qkh3SDVHVWc2UXcwei1QY0szbVJHRWliSGszRHFKaEJWd1lxMWlUWUhJX2QtdVNDRHlEQmd4czlfOXNtTGgyUHRBYndTcldXTWpDWGdkWklocnJZd1BuazhZdkw4NEpZV0tTMVJfX1N1REs1bk1jM0doMzZkc2QxT3JhQy04Y3pZX2FTU1EtZnNvTEV2bHgyUkEwM0xKU0dIRWZHbGwyTFBoVWRBNHRTbmVyYk5iTzQ1WGtKUzJfSDZCN0xObmVzdHJERlQ4WTFxSTBTYUJTWjNqcG9uTEY5QlE1dHRYVVJsWXRVcW1oclFtU0tXZ1k4cTVEWDZHVXkxYS1GenVibGs2ZlY1NkJvNzh5ZUZQVVVXMVFGMWE3VlRqU2gtY1I2c2w1YTMtOUFwSTFtWTRRIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUlPM280dk9MS3g5NTM2SFF6aHhQQkJTUkcwU1FFYVA1NUJSekRHeUNZTzFkdmhMWWlaQ3VNbDVSWkFrNWZNU1R2eXQ5dTd6OEVPVlpCRGdHUGlpQ1dnMzBWSzRvaEEwbmFrZzhoSHNFRDI5WkJYVXU0cFpCWkFROXlGWkJoQ0MwZW1GSmY2WkI1SEhCT2kwTFdEMmFaQ1lzdUE4YU1IWkNpakIxY2RNZGNOZFVTIiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE2NTg3NTcwODN9; fbsr_124024574287414=VmXJSw3u_VYtFOCNOLaM-017qlWsLODsHvTtpzBXn8A.eyJ1c2VyX2lkIjoiNjAyNjE5Nzg2IiwiY29kZSI6IkFRQlkwdXhsbDVBZk5rU2ZsQS00VHIwOTcwSnMxcGt5MXNoQ2lqVFJRb3lQNmM0WExxdFh3aUY0alR2cFhYZk44OTJMV1B3eVVlam1QNjRYV1dxdkdRZC1qYUFQaG8yUjdfYmdJZkozV0V6SkFtWS0ydGhHbWo2N0xENkhvS1VlMURueXZwWU1feWtIQUp1MGVKMHAxRHdYRW5ldEFyVGM4VEdIbHNBSGptU3M2TUFVdW4xdXh1cE9kSnJnbjNDMERJMU0tTXh3MnVkaFRmdHdOVThJUjN5UjYxeWJfTEQ1VTFBRVhZVlVRX0tVdGlpeEEyZWVMVTJ5UTNmVXdNN0RDLTItZGVzM0RuRWl6azVobFk5RHcyc09Pd2plM19BV1VmQnFUc1g4c19DOUE5R2xteTRIa0YyREdWR3VSZVhxNkFjIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUpFTW9KOExYaXo4VkpTWHJLOFpDd0VGZXNIY3pGQ3BGNGl6cnpka2xEWkNnSm1qUHdReVFPcmRwWkJZWkJ2Zmc1cFlUaFFwcmp5WkFqRjdkZzQ3Qk0yaHpmNlpCSUo3cXlmemhlc09aQ1dXbFJaQ1JtMno5Z1JuWWJvTWdic2U1TnMwUVVoZFpDQThlbVpCdnEzTEc5aGxFVG92TE5VUVR0a292a2RsYTc5Z0RGIiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE2NTg3NTYzODZ9; csrftoken=aMSU26xkWCSMqYBqTKfmXU7oypTAX9Od; ig_did=E660B40F-020A-4DC0-9705-60B87B15695C; mid=YuaIrQAEAAEbk7YYopvEnSC49ddI'

def download_html(url):
    print(f'Downloading HTML from: {url}...')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Cookie': get_cookie_header(),
        'X-IG-App-ID': '936619743392459',
    }
    html_page = requests.get(url, headers = headers)
    
    if html_page.status_code == 200:
        content = html_page.text
        if DEBUG:
            write_file(content, 'instagram.html')
        return content
    else:
        print("Couldn't download HTML page :'(")
        return None

def get_item_metadata(item):
    print('Getting iteam metadata...')
    caption = item['caption']
    
    metadata = {}
    metadata['id'] = item['code']
    metadata['uploader_id'] = item['user']['username']
    metadata['title'] = f"Post by {metadata['uploader_id']}"
    metadata['fulltitle'] = metadata['title']
    metadata['description'] = caption['text'] if caption is not None else None
    metadata['timestamp'] = caption['created_at'] if caption is not None else None
    metadata['uploader'] = item['user']['full_name']
    metadata['like_count'] = item['like_count']
    metadata['comment_count'] = item.get('comment_count')
    metadata['extractor'] = 'Instagram'
    metadata['webpage_url'] = f"https://www.instagram.com/p/{metadata['id']}"
    metadata['webpage_url_basename'] = metadata['id']
    metadata['extractor_key'] = 'Instagram'
    metadata['display_id'] = metadata['id']
    metadata['upload_date'] = datetime.fromtimestamp(metadata['timestamp']).strftime("%Y%m%d") if metadata['timestamp'] is not None else None
    
    return metadata

def download_media(url, filename):
    print('Downloading media...')
    image = requests.get(url, stream = True)
    
    if image.status_code == 200:
        image.raw.decode_content = True
        with open(f'{OUTPUT_FOLDER}/{filename}', 'wb') as f:
            print(f'Saving image file: {filename}')
            shutil.copyfileobj(image.raw, f)
    else:
        print("Couldn't download image :'(")

def download_media_info(media_id):
    url = f'https://i.instagram.com/api/v1/media/{media_id}/info/'
    print(f'Downloading media info from: {url}...')
    headers = {
        'Cookie': get_cookie_header(),
        'X-IG-App-ID': '936619743392459'
    }
    media_info = requests.get(url, headers = headers)
    media_info_json = json.loads(media_info.text)
    if DEBUG:
        write_file(media_info_json, 'media_info.json', is_json = True)
    return media_info_json

def write_file(object, filename, is_json = False):
    print(f'Saving file: {filename}...')
    output_text = json.dumps(object, indent = 4) if is_json else object
    with open(f'{OUTPUT_FOLDER}/{filename}', 'w', encoding='utf-8') as f:
        f.write(output_text)

def get_image_url_from_versions(image_versions2, metadata):
    if image_versions2 is None:
        print('No image_versions2 found!')
        return

    candidates = image_versions2['candidates']
    filtered_candidates = [c for c in candidates if c['width'] == metadata['width'] and c['height'] == metadata['height']]
    return candidates[0]['url'] if len(filtered_candidates) == 0 else filtered_candidates[0]['url']

def get_video_url_from_versions(video_versions, metadata):
    if video_versions is None:
        print('No video_versions found!')
        return

    filtered_version = [v for v in video_versions if v['width'] == metadata['width'] and v['height'] == metadata['height']]
    return video_versions[0]['url'] if len(filtered_version) == 0 else filtered_version[0]['url']

def process_carousel(item):
    carousel_media = item.get('carousel_media')

    if carousel_media is None:
        print('No carousel media found!')
        return

    print(f"Processing {item['carousel_media_count']} media item(s) from carousel...")
    for index, cm_item in enumerate(carousel_media):
        process_image(cm_item, carousel_media, index)
        process_video(cm_item, carousel_media, index)

def get_ext_from_url(url):
    return url.split('?')[0].split('.')[-1]

def process_image(item, carousel_media = None, index = None):
    image_versions2 = item.get('image_versions2') if carousel_media is None else carousel_media[index].get('image_versions2')
    if not image_versions2:
        print('No image data to process')
        return

    print('Processing image...')
    media_type = item['media_type']
    print(f'Media type: {media_type}')
    metadata['width'] = item.get('original_width') if carousel_media is None else carousel_media[index].get('original_width')
    metadata['height'] = item.get('original_height') if carousel_media is None else carousel_media[index].get('original_height')
    url = get_image_url_from_versions(image_versions2, metadata)
    metadata['url'] = url
    metadata['ext'] = get_ext_from_url(url)
    base_filename = f"{metadata['uploader_id']} - {metadata['id']}"
    image_filename = f"{base_filename}.{metadata['ext']}" if index is None else f"{base_filename} - {index + 1}.{metadata['ext']}"
    download_media(url, image_filename)
    write_file(metadata, f"{base_filename}.info.json", is_json = True)

def process_video(item, carousel_media = None, index = None):
    video_versions = item.get('video_versions') if carousel_media is None else carousel_media[index].get('video_versions')
    if not video_versions:
        print('No video data to process')
        return

    media_type = item['media_type']
    print(f'Media type: {media_type}')
    metadata['width'] = item.get('original_width') if carousel_media is None else carousel_media[index].get('original_width')
    metadata['height'] = item.get('original_height') if carousel_media is None else carousel_media[index].get('original_height')
    metadata['duration'] = item.get('video_duration') if carousel_media is None else carousel_media[index].get('video_duration')
    url = get_video_url_from_versions(video_versions, metadata)
    metadata['url'] = url
    metadata['ext'] = get_ext_from_url(url)
    base_filename = f"{metadata['uploader_id']} - {metadata['id']}"
    image_filename = f"{base_filename}.{metadata['ext']}" if index is None else f"{base_filename} - {index + 1}.{metadata['ext']}"
    download_media(url, image_filename)
    write_file(metadata, f"{base_filename}.info.json", is_json = True)

### Command Line input

#if len(sys.argv) < 2:
#   print('Error, no IG ID found!')
#   exit(0)

#igid = sys.argv[1]

### urls.txt file input

# urls = []
# with open('urls.txt') as f:
#     urls = f.read().splitlines()

# for url in urls:
#     html_data = download_html(url)
#     media_id = re.search(r'"media_id":"([0-9]*)"', html_data, re.M).group(1)
#     media_info = download_media_info(media_id)
    
#     for item in media_info.get('items', []):
#         print('Processing item from data loaded...')
#         metadata = get_item_metadata(item)
#         process_image(item)
#         process_video(item)
#         process_carousel(item)
#         with open("success.txt", "a") as myfile:
#             myfile.write(f'{url}\n')

### media_ids.txt file input

media_ids = []
with open('media_ids.txt') as f:
    media_ids = f.read().splitlines()

for media_id in media_ids:
    media_info = download_media_info(media_id)
    
    for item in media_info.get('items', []):
        print('Processing item from data loaded...')
        metadata = get_item_metadata(item)
        process_image(item)
        process_video(item)
        process_carousel(item)
        with open("success.txt", "a") as myfile:
            myfile.write(f'{media_id}\n')
