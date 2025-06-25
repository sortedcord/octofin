import os.path
from io import BytesIO
from PIL import Image
import pykakasi
import requests

def japanese_to_romaji(text: str) -> str:
    kakasi = pykakasi.kakasi()
    kakasi.setMode("H", "a")  # Hiragana to ascii
    kakasi.setMode("K", "a")  # Katakana to ascii
    kakasi.setMode("J", "a")  # Kanji to ascii
    kakasi.setMode("r", "Hepburn")  # Use Hepburn Romanization
    kakasi.setMode("s", True)  # Add space between words
    converter = kakasi.getConverter()

    return converter.do(text)

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
