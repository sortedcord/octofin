import os.path
from io import BytesIO
from PIL import Image
import cutlet
import requests
from enum import  Enum
from config.utils import get_config
import re


class DownloaderError(Enum):
    PO_TOKEN_NOT_AVAILABLE = 'A GVS PO Token has not been provided. You may not be able to download the best audio quality available.'
    COOKIES_PATH_NOT_AVAILABLE = 'Path to cookies file has not been provided. You may not be able to download the best audio quality available.'
    INVALID_COOKIE_DATA = 'The cookie file provided has invalid data. You may not be able to download the best audio quality available.'
    INVALID_OUTPUT_LOCATION = 'Output location provided is either invalid or not accessible.'

def downloader_availability() -> DownloaderError|int:
    output_directory = get_config('OCTO_OUTPUT_DIR')
    po_token = get_config('PO_TOKEN')
    cookies_path = get_config('COOKIES_PATH')

    if output_directory is None:
        return DownloaderError.INVALID_OUTPUT_LOCATION

    if not os.path.exists(output_directory):
        return DownloaderError.INVALID_OUTPUT_LOCATION

    if cookies_path is None or cookies_path=="":
        return DownloaderError.COOKIES_PATH_NOT_AVAILABLE
    if not os.path.exists(cookies_path):
        return DownloaderError.COOKIES_PATH_NOT_AVAILABLE
    try:
        with open(cookies_path) as f:
            data = f.read()
            if data.strip() == "":
                return DownloaderError.INVALID_COOKIE_DATA
    except:
        return DownloaderError.INVALID_COOKIE_DATA
    if po_token is None or po_token== "":
        return DownloaderError.PO_TOKEN_NOT_AVAILABLE

    return 1


def japanese_to_romaji(text: str) -> str:
    katsu = cutlet.Cutlet()
    converted = (katsu.romaji(text))
    print(converted)
    return converted

def crop_to_square_bytes(image_bytes: bytes) -> bytes:
    # Load image from bytes
    image = Image.open(BytesIO(image_bytes))

    width, height = image.size

    if width != height:
        side_length = min(width, height)
        left = (width - side_length) // 2
        top = (height - side_length) // 2
        right = left + side_length
        bottom = top + side_length
        image = image.crop((left, top, right, bottom))

    # Save image to a new BytesIO buffer
    buffer = BytesIO()
    image_format = image.format or 'PNG'  # Use original format, default to PNG
    image.save(buffer, format=image_format)
    return buffer.getvalue()

def read_changelog(changelog_location = 'changelog.md') -> (str,str):
    if os.path.exists('/app/changelog.md'):
        changelog_location = '/app/changelog.md'

    if not os.path.exists(changelog_location):
        data = requests.get("https://raw.githubusercontent.com/sortedcord/octofin/refs/heads/master/changelog.md")
        print("Fetching changelog")
        with open(changelog_location, 'w') as f:
            f.write(data.text)

    with open(changelog_location) as f:
        raw_markdown = f.read()

    version_data = raw_markdown.split("## [")[1:]

    versions = []

    for _version in version_data:
        tag_list = {
            'Added': [],
            'Changed': [],
            'Fixed': []
        }
        for tag, points in tag_list.items():
            raw_points:str = _version.split(f"### {tag}\n")[-1].split("\n###")[0]

            for point in raw_points.split("\n"):
                if point == "":
                    continue
                tag_list[tag].append(point.replace('- ', ''))

        versions.append({
            'version': _version.split("]")[0],
            'date': _version.split("- ")[1].split("\n")[0],
            'tag_list': tag_list
        })


    return versions


def download_image_bytes(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def classify_youtube_music_list(url:str) -> (str, str):
    from urllib.parse import urlparse, parse_qs

    query = parse_qs(urlparse(url).query)
    playlist_id = query.get("list", [""])[0]

    if playlist_id.startswith("OL"):
        return "album", playlist_id
    elif playlist_id.startswith("RD") or playlist_id.startswith("PL") or playlist_id.startswith("VL"):
        return "playlist", playlist_id
    else:
        return "unknown", playlist_id


def update_googleusercontent_url(url:str, width:int, height:int, quality:int) -> None|str:
    """
    Update a Googleusercontent image URL with new width, height, and quality values.

    Args:
        url (str): The original URL.
        width (int): Desired width.
        height (int): Desired height.
        quality (int): Desired quality (used in the 'l' parameter).

    Returns:
        str or None: Modified URL if pattern matches, else None.
    """
    pattern = r'(https://lh3\.googleusercontent\.com/[\w\-]+)=w\d+-h\d+-l\d+-'

    if not re.match(pattern, url):
        return None

    updated_url = re.sub(
        r'=w\d+-h\d+-l\d+-',
        f'=w{width}-h{height}-l{quality}-',
        url
    )

    return updated_url

def fetch_lyrics():
    # TODO: Make use of a lyrics provider
    return
