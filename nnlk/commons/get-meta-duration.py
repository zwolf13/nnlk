import os
import json

for filename in os.listdir('/srv/dev-disk-by-uuid-FE5A2CD05A2C880B/NNLK_NEW/ZWOLF_HOME/_Nanalka/new/videos/youtube'):
    if not filename.endswith('.json'):
        continue
    with open(filename, 'r', encoding='utf-8') as my_file:
        content = my_file.read()
        my_json = json.loads(content)
        duration = my_json.get('duration')
        print(f'{filename} => {duration}')
