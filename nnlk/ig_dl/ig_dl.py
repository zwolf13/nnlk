import re
import requests
import json
import shutil
import sys
from datetime import datetime
from http.cookiejar import MozillaCookieJar

# TODO Include {UPLOADER} in the output folder
OUTPUT_FOLDER = 'C:/Users/Mauricio/dwhelper/Instagram'
DEBUG = False

def get_cookie_header():
    return 'rur="NCG\0543452129080\0541740688100:01f70dda2601fc8793b2e072be66f0122ab0060cff7bcf8e7036bbb49daff72cb36ef3e5"; csrftoken=w8kK63oJgsxo6eXN1udEKHYSbSta79PA; mid=Zd5apAAEAAHMQ9fP8tgmuQJgwGLW; ps_l=0; ps_n=0; ig_did=32C1E0C7-F309-4D8F-93AD-1D2DA788C3B1; ig_nrcb=1; datr=1pTfZap-02W4jDPhhgBzwwYf; ds_user_id=3452129080; sessionid=3452129080%3AIzJpD6z6fEQRi9%3A7%3AAYfUrcf8Ye33CZUq0_L99EaKNrKJ8sF6Wp9sN5qLsQ; shbid="19869\0543452129080\0541740688090:01f7c126a7ee5704c9198691d7b3e71c46729cee7be4cdf1ee87b6ed3e3de60b3b1b1192"; shbts="1709152090\0543452129080\0541740688090:01f7fd73865a14bcdaf96be1a6b62cb53726f6d36691999afedfc17afc5fa61ff9ddf678"'

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
