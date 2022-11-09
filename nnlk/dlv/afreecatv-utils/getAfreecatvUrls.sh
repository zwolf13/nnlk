#!/bin/bash

INPUT_FILE="playlists.txt";
OUTPUT_FILE="afreecatv.urls.txt";
BASE_URL="https://stbbs.afreecatv.com/api/get_vod_list.php?szDataType=PLAYLIST&nTitleNo=65364878&szBjId=clsz0409&nPlaylistIdx=";

while read -r playlist_id
do
    echo "Fetching playlist: ${playlist_id}...";
    # Setting up file names
    TMP_FILE="${playlist_id}.tmp";
    JSON_FILE="${playlist_id}.tmp.json";
    URL_FILE="${playlist_id}.tmp.url";

    wget --quiet -O "${TMP_FILE}" "${BASE_URL}${playlist_id}";
    cat "${TMP_FILE}" | python3 -m json.tool > "${JSON_FILE}";
    python3 getVideoUrls.py "${JSON_FILE}" > "${URL_FILE}";
done < "playlists.txt"

echo "Consolidating URLs...";
cat *.tmp.url | sort -u > "${OUTPUT_FILE}";

echo "Removing temporal files...";
rm *.tmp *.tmp.json *.tmp.url;

echo "All done!";
