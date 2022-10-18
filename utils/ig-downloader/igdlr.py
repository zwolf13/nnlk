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
    return 'csrftoken=aMSU26xkWCSMqYBqTKfmXU7oypTAX9Od; mid=YtVnLAAEAAGwNT-WIsVuz-ohGSs5; ig_did=C3D3162C-1019-4012-87A4-1DB6201F23B1; ig_nrcb=1; ds_user_id=3452129080; sessionid=3452129080%3AQviA2eUVAUMZVb%3A6%3AAYeSasN7kXGs7vH5bagdOH0meIA8fmxtd2QDi6BfpQ; shbid="19869\0543452129080\0541690297172:01f73a9c6de88e8e3657b9138a3a7e6514cc06a7c5d66d3279e9ba4d29c9826eebdc2c8e"; shbts="1658761172\0543452129080\0541690297172:01f779128f5c59d2a8690d0cc5679e087b95f0f7ceca16478203a9db176c5ede3930ee71"; datr=eWfVYnecei_NfGDgohf3_lJV; fbm_124024574287414=base_domain=.instagram.com; rur="NCG\0543452129080\0541690298835:01f712db339d4ee4ea98a7a1b9bdaf48913d22cc614258d59072f19699b7f918bbd16132"; fbsr_124024574287414=xrSBpBpkXf_fJx87vWZ4QgnocY-cwI1aADccfIEXSDQ.eyJ1c2VyX2lkIjoiNjAyNjE5Nzg2IiwiY29kZSI6IkFRQnF2dllXU2QtY1NQRWV6d3BZOXpyNlJXY21uRl9FOWQ1TXBjWlZvX1l3UkFTQnB0T3FqUlhFdEE4VXVjTnVtYWFoT2JpTTM4TF9kTnB2QzFLVG5ubE56S1RtSWxfTGRveFBYVFN5dDVCd05wdE4xVUNFMmtBeS1BZmxfQ3FNUjZ6OG9wSFlWN093MzR5OXJ3YjQ3VnUtNXlaRjdLQnlYZFItbDgxVVFueTBFaHZCb1I0QXJVLS1VOG9BU014Q1FLTGpvRHpjM21jTnd3Tjc5SS0xUHBGMGtrX1FqMzFIaEpqemwyQTN5a1NhWThadWpDR0VrdHYwLVozeDRncUFEZWZhTVNiZzNvTDZkV1o5TkwySE5naVMxRGFrU3lKSUplLWtqUS1rajkzSVdTRklSYlpOek9lLUZuX2llMWdIc0dJIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQU1KNXBvUWxnUmF2OXFmaHU4Z29Fd2Z0MnV1bElIN0hUeGhvRVRUZHRIdnVRNzdNSFJ6WDU3MWc2TUYxdHRQQjcyaEtJcHdodkFzSjNtRzc5S0toNTJiYkNpbmlwN3dJbVVYUzNrMkFEMFZPZ3R5WkE0anZoS0NlR0ZaQk13UVVFb2NuSXRUY0JSR244dFpCajVSS21CQndYOXBkTDYwc0RyTWxlMVYiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTY1ODc2MjgxOH0'

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