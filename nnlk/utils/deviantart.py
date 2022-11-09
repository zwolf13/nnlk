import json;
from jsonpath_ng import jsonpath;
from jsonpath_ng.ext import parse; # https://github.com/h2non/jsonpath-ng/issues/8

with open('deviantart.json') as f:
    json_file = json.load(f);

[result.value for result in parse('$.results[?(is_favourited == false & category != "Literature" & category != "Romance" & category != "General Fiction")][url]').find(json_file)]
