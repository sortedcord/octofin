import json
import os

import yt_dlp

from config.utils import get_config
from downloader.models import DictionaryKey


def get_yt_data(url:str) -> dict:
    save_to_disk:bool = get_config('STORE_FETCHED_METADATA')

    os.makedirs('temp/', exist_ok=True)

    v_id = "error43"
    if "?v=" in url:
        v_id = url.split("?v=")[-1].split("&")[0]
    if "?list" in url:
        v_id = url.split("?list=")[-1].split("&")[0]

    if save_to_disk:
        file = f'temp/{v_id}.json'
        if os.path.exists(file):
            raw_data = json.loads(open(file).read())
            return extract_data(raw_data)

    cookies_path = get_config('COOKIES_PATH')
    po_token = get_config('PO_TOKEN')

    ydl_opts = {
        'cookiefile': f'{cookies_path}',
        'extract_flat': 'discard_in_playlist',
        'extractor_args': {
            'youtube': {
                'po_token': [f'web_music.gvs+{po_token}']
                }
            },
        }


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        _info:dict = ydl.extract_info(url, download=False) # type: ignore

    if save_to_disk:
        with open(file, 'w') as f:
            f.write(json.dumps(_info, indent=2))

    if _info['title'].startswith('Album - '):
        process_album(_info)

    return extract_data(_info)

def process_album():

    return


def download_song(info:dict) -> str:
    cookies_path:str = get_config("COOKIES_PATH")
    po_token:str = get_config("PO_TOKEN")

    ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f"temp/{ info['track_number']}. {info['title'].replace('/', '_')}",
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'opus',
                    'preferredquality': '0',
                }],
                'cookiefile': f'{cookies_path}',
                'extract_flat': 'discard_in_playlist',
                'extractor_args': {
                    'youtube': {
                        'po_token': [f'web_music.gvs+{po_token}']
                        }
                    },
            }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        temp_file = ydl.prepare_filename(info['a_info']) + '.opus'
        if not os.path.exists(temp_file):
            error_code = ydl.download(info['url'])
            print(error_code)

    return temp_file


def extract_data(raw_data:dict) -> dict:
    info = {
        'a_info': raw_data,
        'url': f"https://music.youtube.com/watch?v={raw_data['id']}",
        'title': raw_data['title'],
        'album': raw_data['album'] if 'album' in raw_data else raw_data['title'],
        'track_number': 1,
        'genres': []
    }

    try:
        thumbnail = raw_data['thumbnails'][0]['url']
    except KeyError or IndexError:
        thumbnail = raw_data['thumbnail']

    if thumbnail.endswith('-rj'):
        thumbnail = thumbnail.split("=w")[0] +'=w1400-h1400-l100'
    else:
        thumbnail = raw_data['thumbnail']
    info['cover'] = thumbnail

    if 'release_date' not in raw_data:
        info['release_date'] = f"{raw_data['upload_date'][:4]}-{raw_data['upload_date'][4:6]}-{raw_data['upload_date'][6:]}"
    else:
        info['release_date'] = f"{raw_data['release_date'][:4]}-{raw_data['release_date'][4:6]}-{raw_data['release_date'][6:]}"

    if 'artists' in raw_data:
        info['artists'] = raw_data['artists']
    else:
        info['artists'] = [raw_data['channel']]

    info['album_artists'] = [info['artists'][0]]

    dictionary = DictionaryKey.objects.all()
    for key, value in info.items():
        for dictionary_key in dictionary:
            if dictionary_key.to_replace in value:
                info[key] = value.replace(dictionary_key.to_replace, dictionary_key.replacement)

    return info
