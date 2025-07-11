import json
import os

import yt_dlp

from config.utils import get_config
from downloader.models import DictionaryKey, DownloadTask
from ytmusicapi import YTMusic
from .utils import classify_youtube_music_list


def fetch_info_dict(url:str) -> dict:
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
        _info:dict = ydl.extract_info(url, download=False)

    return _info


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

    _info = fetch_info_dict(url)

    return extract_data(_info)

def process_album(_info):
    return

def process_playlist_metadata(task:DownloadTask):
    # TODO: Revert to single file processing if only 1 track in playlist/album
    try:
        ytmusic = YTMusic()
    except Exception as e:
        task.status = 'failed'
        task.save()
        raise e

    task.download_item, playlist_id = classify_youtube_music_list(task.url)
    task.save()

    playlist_data = ytmusic.get_playlist(playlist_id)
    tracks = []

    # Process tracks
    for track_data in playlist_data['tracks']:
        tracks.append({
            'url':f"https://music.youtube.com/watch?v={track_data['videoId']}",
            'title': track_data['title'],
            'artists': [artist['name'] for artist in track_data['artists']],
            'album_artists':  [artist['name'] for artist in track_data['artists']][0],
            'album': track_data['album']['name'],
            'cover': track_data['thumbnails'][0],
            'release_date': f"01-01-{playlist_data['year']}" if 'year' in playlist_data else "01-01-2001",
            'genres': []
        })

    # Handle for album
    if task.download_item == 'album':
        album_browse_id = ytmusic.get_album_browse_id(playlist_id)
        _data = ytmusic.get_album(album_browse_id)
        thumbnail = _data['thumbnails'][0]['url']
        album_release_date = f"01-01-{_data['year']}"

        for track in tracks:
            track['album'] = _data['title']
            track['album_artists'] = [artist['name'] for artist in _data['artists']]
            track['release_date'] = album_release_date

        album_data = {
            'title': _data['title'],
            'cover': thumbnail,
            'release_date': album_release_date,
            # TODO: Get correct date
            'tracks': tracks
        }

        task.metadata = album_data
        task.save()
        return

    task.metadata = {
        'title': playlist_data['title'],
        'description': playlist_data['description'],
        'cover': playlist_data['thumbnails'][0]['url'],
        'tracks':tracks,
    }
    task.save()
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
