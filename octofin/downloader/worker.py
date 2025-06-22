import yt_dlp
import json
import os
from mutagen.oggopus import OggOpus
import base64
import struct
import requests
import shutil


COOKIES_PATH = os.getenv('COOKIES_PATH')
PO_TOKEN = os.getenv('PO_TOKEN')
OUTPUT_DIR = os.getenv('OCTO_OUTPUT_DIR')


def download_image_bytes(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def getytdata(url:str) -> dict:
    os.makedirs('temp/', exist_ok=True)
    ydl_opts = {
        'cookiefile': f'{COOKIES_PATH}',
        'extract_flat': 'discard_in_playlist',
        'extractor_args': {
            'youtube': {
                'po_token': [f'web_music.gvs+{PO_TOKEN}']
                }
            },
        }
    
    v_id = url.split("?v=")[-1].split("&")[0]
    file = f'temp/{v_id}.json'
    
    if os.path.exists(file):
        return json.loads(open(file).read())

    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        _info:dict = ydl.extract_info(url, download=False) # type: ignore
    
    # open('raw_data.json', 'w').write(json.dumps(_info, indent=2))
    
    
    info = {
        'a_info': _info,
        'url': url,
        'title': _info['title'],
        'artists': _info['artists'],
        'release_date': f"{_info['release_date'][:4]}-{_info['release_date'][4:6]}-{_info['release_date'][6:]}",
        'cover': _info['thumbnails'][0]['url'].split("=w")[0] +'=w1400-h1400-l100',
        'album': _info['album'] if 'album' in _info else _info['title'],
        'album_artists': [_info['artists'][0]],
        'track_number': 1,
        'genres': []
    }
    print("Writing to file")
    with open(file, 'w') as f:
        f.write(json.dumps(info, indent=2))

    return info

def download_song(info:dict) -> str:
    ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f"temp/{ info['track_number']}. {info['title'].replace('/', '_')}",
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'opus',
                    'preferredquality': '0',
                }],
                'cookiefile': f'{COOKIES_PATH}',
                'extract_flat': 'discard_in_playlist',
                'extractor_args': {
                    'youtube': {
                        'po_token': [f'web_music.gvs+{PO_TOKEN}']
                        }
                    },
            }
            
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        temp_file = ydl.prepare_filename(info['a_info'])
        error_code = ydl.download(info['url'])
        print(error_code)
        print(temp_file)
    
    return temp_file
        
def apply_metadata(file, info):
    audio = OggOpus(file)
    
    # Initialize tags if missing
    if audio.tags is None:
        audio.add_tags()
    
    tags = audio.tags

    if info.get('title'):
        tags['title'] = [info['title']]
    if info.get('artists'):
        tags['artist'] = info['artists']
    if info.get('album'):
        tags['album'] = [info['album']]
    if info.get('album_artists'):
        tags['albumartist'] = info['album_artists']
    if info.get('genres'):
        tags['genre'] = info['genres']
    if info.get('track_number'):
        tags['tracknumber'] = [str(info['track_number'])]

    # Handle cover art from URL
    cover_url = info.get('cover')
    if cover_url:
        cover_data = download_image_bytes(cover_url)  # Download image as bytes

        # Create METADATA_BLOCK_PICTURE structure (type 3 = front cover, mime type guessed as jpeg)
        mime = 'image/jpeg'
        if cover_url.lower().endswith('.png'):
            mime = 'image/png'
        picture = struct.pack('>I', 3)  # Picture type (front cover)
        picture += struct.pack('>I', len(mime)) + mime.encode('utf-8')
        picture += struct.pack('>I', 0)  # Description length
        picture += struct.pack('>III', 0, 0, 0)  # Width, height, depth
        picture += struct.pack('>I', 0)  # Colors
        picture += struct.pack('>I', len(cover_data)) + cover_data

        encoded_picture = base64.b64encode(picture).decode('ascii')
        tags['metadata_block_picture'] = [encoded_picture]

    audio.save()


def import_song(file_path, info):
    """
    Moves the file from its current path to temp/{ALBUM ARTIST[0]}/[{YEAR}] {ALBUM}/

    Args:
        file_path (str): Current path of the file
        info (dict): Metadata dictionary containing at least 'album_artists', 'album', and 'release_date' or 'year'
    """
    # Extract album artist, album, and year
    album_artists = info.get('album_artists', [])
    album_artist = album_artists[0] if album_artists else 'Unknown Artist'

    album = info.get('album', 'Unknown Album').replace('/', '_')

    # Try to get year from release_date or year key
    year = 'Unknown Year'
    if 'release_date' in info and info['release_date']:
        year = str(info['release_date'])[:4]
    elif 'year' in info and info['year']:
        year = str(info['year'])

    # Construct destination directory
    dest_dir = os.path.join(OUTPUT_DIR, album_artist, f'[{year}] {album}') # type: ignore

    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Get the filename from the file_path
    filename = os.path.basename(file_path)

    # Construct destination file path
    dest_path = os.path.join(dest_dir, filename)

    # Move the file
    shutil.move(file_path, dest_path)

    return dest_path