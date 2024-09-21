#!/bin/bash

SESSION_ID="3452129080%3A7QiLaQ8gIDSzuG%3A0%3AAYf84Ke77ut5ra6oZuHb3kLtl4GMnfmd7u_gzKugDCM"
COOKIE='Cookie: rur="NCG\0543452129080\0541740688100:01f70dda2601fc8793b2e072be66f0122ab0060cff7bcf8e7036bbb49daff72cb36ef3e5"; csrftoken=w8kK63oJgsxo6eXN1udEKHYSbSta79PA; mid=Zd5apAAEAAHMQ9fP8tgmuQJgwGLW; ps_l=0; ps_n=0; ig_did=32C1E0C7-F309-4D8F-93AD-1D2DA788C3B1; ig_nrcb=1; datr=1pTfZap-02W4jDPhhgBzwwYf; ds_user_id=3452129080; sessionid=3452129080%3AIzJpD6z6fEQRi9%3A7%3AAYfUrcf8Ye33CZUq0_L99EaKNrKJ8sF6Wp9sN5qLsQ; shbid="19869\0543452129080\0541740688090:01f7c126a7ee5704c9198691d7b3e71c46729cee7be4cdf1ee87b6ed3e3de60b3b1b1192"; shbts="1709152090\0543452129080\0541740688090:01f7fd73865a14bcdaf96be1a6b62cb53726f6d36691999afedfc17afc5fa61ff9ddf678"'

# Files
OUTPUT="media-ids.txt"
ERROR="error.txt"
TMP="instagram.tmp"

> "${OUTPUT}"
> "${ERROR}"

while read url;
do
    echo "Working on ${url}..."
    # curl --silent -H "Cookie: sessionid=${SESSION_ID}" "${url}" > "${TMP}"
    curl --silent -H "${COOKIE}" "${url}" > "${TMP}"
    # grep -oe "\"media_id\":\"[0-9]*\"" instagram.tmp | head -n 1 | grep -oe "[0-9]*" >> "${OUTPUT}"
    media_id=`grep -oe "\"media_id\":\"[0-9]*\"" instagram.tmp | head -n 1 | grep -oe "[0-9]*"`;
    if [ -z "${media_id}" ]
    then
        echo "${url}" >> "${ERROR}"
    else
        echo "${media_id}" >> "${OUTPUT}"
    fi
done < urls.txt

rm "${TMP}"
