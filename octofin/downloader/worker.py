import os
from mutagen.oggopus import OggOpus
import base64
import struct
import shutil
from .utils import crop_to_square_bytes, download_image_bytes
from config.utils import get_config

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
    if info.get('lyrics'):
        tags['lyrics'] = [info['lyrics']]

    # Handle cover art from URL
    cover_url = info.get('cover')
    if cover_url:
        cover_data = download_image_bytes(cover_url)  # Download image as bytes

        if not cover_url.endswith('-rj'):
            cover_data = crop_to_square_bytes(cover_data)

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

    year = 'Unknown Year'
    if 'release_date' in info and info['release_date']:
        year = str(info['release_date'])[:4]
    elif 'year' in info and info['year']:
        year = str(info['year'])

    output_dir = get_config('OCTO_OUTPUT_DIR')
    dest_dir = os.path.join(output_dir, album_artist, f'[{year}] {album}') # type: ignore

    os.makedirs(dest_dir, exist_ok=True)
    filename = os.path.basename(file_path)
    dest_path = os.path.join(dest_dir, filename)
    shutil.move(file_path, dest_path)

    return dest_path