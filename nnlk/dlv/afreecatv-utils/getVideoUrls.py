#!/usr/bin/python3

import sys;
import json;
from jsonpath_ng import jsonpath, parse;

playlist_file = sys.argv[1];

with open(playlist_file) as f:
    json_file = json.load(f);
    json_path = parse('$.data.title_playlist.list[*].title_no');
    [print("https://vod.afreecatv.com/player/" + format(match.value)) for match in json_path.find(json_file)];
