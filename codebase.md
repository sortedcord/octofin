# Dockerfile

```
# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Prevents Python from writing pyc files to disk and buffers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y ffmpeg

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (including the octofin Django project)
COPY . /app/

EXPOSE 8193

RUN python /app/octofin/manage.py makemigrations
RUN python /app/octofin/manage.py makemigrations likedplaylist
RUN python /app/octofin/manage.py makemigrations downloader
RUN python /app/octofin/manage.py migrate

# Use Gunicorn as the entrypoint, point to the wsgi.py inside the Django project
CMD ["gunicorn", "--chdir", "octofin", "--bind", "0.0.0.0:8193", "octofin.wsgi:application"]

```

# octofin/config/__init__.py

```py

```

# octofin/config/admin.py

```py
# config/admin.py
from django.contrib import admin
from .models import GlobalConfig

@admin.register(GlobalConfig)
class GlobalConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
    search_fields = ('key',)

```

# octofin/config/apps.py

```py
from django.apps import AppConfig


class ConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'

```

# octofin/config/context_processor.py

```py
# config/context_processors.py
from .utils import get_config

def global_config(request):
    return {
        'SITE_NAME': get_config('SITE_NAME', 'Octofin'),
        'FOOTER_TEXT': get_config('FOOTER_TEXT', ''),
        # Add other frequently accessed configs here
    }

```

# octofin/config/models.py

```py
from django.db import models

class GlobalConfig(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.key
```

# octofin/config/tests.py

```py
from django.test import TestCase

# Create your tests here.

```

# octofin/config/utils.py

```py
# config/utils.py
from django.core.cache import cache
from .models import GlobalConfig

def get_config(key, default=None):
    # Check cache first
    if cached := cache.get(f'config_{key}'):
        return cached

    try:
        value = GlobalConfig.objects.get(key=key).value
        cache.set(f'config_{key}', value, timeout=60*60)  # Cache 1 hour
        return value
    except GlobalConfig.DoesNotExist:
        cache.set(f'config_{key}', default, timeout=60*60)
        return default

```

# octofin/config/views.py

```py
from django.shortcuts import render

# Create your views here.

```

# octofin/downloader/__init__.py

```py

```

# octofin/downloader/admin.py

```py
from django.contrib import admin
from .models import  DictionaryKey

admin.site.register(DictionaryKey)
# Register your models here.

```

# octofin/downloader/apps.py

```py
from django.apps import AppConfig


class DownloaderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'downloader'

```

# octofin/downloader/context_processors.py

```py
from .utils import read_changelog

def footer_version(request):
    current_version = read_changelog()[0]
    return {
        'current_version' : current_version
    }
```

# octofin/downloader/models.py

```py
from django.db import models

class DictionaryKey(models.Model):
    to_replace =  models.CharField(max_length=255)
    replacement = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.to_replace} -> {self.replacement}"

class DownloadTask(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('fetching', 'Fetching Metadata'),
        ('ready', 'Ready for Edit'),
        ('editing', 'Editing Metadata'),
        ('downloading', 'Downloading'),
        ('importing', 'Importing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    
    url = models.URLField()
    title = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # Store fetched metadata

```

# octofin/downloader/static/downloader/darkmode.js

```js
function setTheme() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
}
setTheme();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', setTheme);

// Auto-switch to dark mode if the user prefers it
const htmlElement = document.documentElement;
const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
if (prefersDark) {
    htmlElement.setAttribute('data-bs-theme', 'dark');
} else {
    htmlElement.setAttribute('data-bs-theme', 'light');
}
```

# octofin/downloader/static/downloader/romanization.js

```js
// Generalized romanize function
function romanize(elementId, replace=false) {
    const element = document.getElementById(elementId);
    return fetch('/ytm/romanize/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: `lyrics=${encodeURIComponent(element.value)}`
    })
        .then(response => response.json())
        .then(data => {
            if (data.romanized) {
                if (replace) {
                    element.value = data.romanized;
                }
                return data.romanized;
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        });
}

function append_romanization(elementId, button) {
    const element = document.getElementById(elementId);
    if (!element) return;

    // Optional: handle button loading state
    let originalText;
    if (button) {
        originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
        button.disabled = true;
    }

    romanize(elementId)
        .then(romanized => {
            const currentValue = element.value.trim();
            const separator = currentValue ? ' / ' : '';
            element.value = currentValue + separator + romanized;
        })
        .catch(error => {
            alert('Error: ' + error.message);
        })
        .finally(() => {
            if (button) {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        });
}
```

# octofin/downloader/tests.py

```py
from django.test import TestCase

# Create your tests here.

```

# octofin/downloader/urls.py

```py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('task/create/', views.create_task, name='create_task'),
    path('edit/<int:task_id>/', views.edit, name='edit'),
    # path('download/', views.download, name='download'),
    path('settings/', views.settings, name='settings'),
    path('automation/', views.automation_view, name='automation'),
    path('queue-status/', views.queue_status, name='queue_status'),
    path('task/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/clear/', views.clear_tasks, name='clear_tasks'),
    path('romanize/', views.romanize, name='romanize'),
]
```

# octofin/downloader/utils.py

```py
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

```

# octofin/downloader/views.py

```py
from django.shortcuts import render, redirect, get_object_or_404
from .worker import getytdata, download_song, apply_metadata, import_song
from .models import DownloadTask
import threading
import os
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .utils import japanese_to_romaji, read_changelog


def home(request):
    tasks = DownloadTask.objects.all().order_by('-created_at')
    changelog_data = read_changelog()
    current_version = changelog_data[0]['version']
    return render(request, "downloader/index.html",
                  {
                      'tasks': tasks,
                      'current_version':current_version,
                      'changelog': changelog_data
                  })


def create_task(request):
    if request.method == "POST":
        url = request.POST.get('url', '').strip()
        if not url.startswith('https://music.youtube.com/'):
            messages.error(request, "Invalid URL. Please enter a YouTube Music URL.")
            return redirect('home')
        if 'playlist?list=' in url:
            messages.error(request, "Playlists are not supported yet.")
            return redirect('home')
        task = DownloadTask.objects.create(url=url, status='fetching')
        threading.Thread(target=fetch_metadata, args=(task.id,)).start()
        return redirect('home')
    return redirect('home')


def fetch_metadata(task_id):
    task = DownloadTask.objects.get(id=task_id)
    try:
        metadata = getytdata(task.url)
        task.metadata = metadata # type: ignore
        task.title = metadata.get('title', 'Unknown Title')
        task.status = 'ready'
        task.save()
    except Exception as e:
        print(e)
        task.status = 'failed'
        task.error = str(e) # type: ignore
        task.save()
        raise e


def edit(request, task_id):
    task = get_object_or_404(DownloadTask, id=task_id)
    
    if request.method == "POST":
        if 'delete_task' in request.POST:
            task.delete()
            return redirect('home')
        
        if 'save_download' in request.POST:
            edited_data = {
                'title': request.POST.get('title'),
                'artists': [a.strip() for a in request.POST.get('artists', '').split(',') if a.strip()],
                'album': request.POST.get('album'),
                'album_artists': [a.strip() for a in request.POST.get('album_artists', '').split(',') if a.strip()],
                'genres': [g.strip() for g in request.POST.get('genres', '').split(',') if g.strip()],
                'track_number': request.POST.get('tracknumber'),
                'cover': request.POST.get('cover'),
                'url': request.POST.get('url'),
                'release_date': request.POST.get('release_date'),
                'lyrics': request.POST.get('lyrics')
            }
            
            for key, value in edited_data.items():
                task.metadata[key] = value # type: ignore
            
            # Start download in background
            task.status = 'downloading'
            task.title = task.metadata['title']
            task.save()
            threading.Thread(target=process_download, args=(task.id,)).start() # type: ignore
            
            return redirect('home')
    
    context = task.metadata
    context['task_id'] = task_id
    return render(request, 'downloader/edit.html', context)
        

def process_download(task_id):
    task = DownloadTask.objects.get(id=task_id)
    try:
        # Use edited metadata if available
        info = task.metadata
                
        # Download and process
        file_path = download_song(info)
        task.status = 'importing'
        task.save()
        apply_metadata(file_path, info)
        import_song(file_path, info)
        
        task.status = 'completed'
        task.save()
    except Exception as e:
        print(e)
        task.status = 'failed'
        task.save()

def queue_status(request):
    status_mapping = dict(DownloadTask.STATUS_CHOICES)
    tasks = DownloadTask.objects.all().values('id', 'status', 'title')
    task_list = []
    for task in tasks:
        task_list.append({
            'id': task['id'],
            'title': task['title'],
            'status': task['status'],
            'status_display': status_mapping.get(task['status'], task['status'])
        })
    return JsonResponse(task_list, safe=False)


@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(DownloadTask, id=task_id)
    task.delete()
    return redirect('home')

@require_POST
def clear_tasks(request):
    from .models import DownloadTask
    DownloadTask.objects.all().delete()
    return redirect('home')

def settings(request):
    cookies_path:str = os.getenv('COOKIES_PATH')
    if cookies_path is not None and os.path.exists(cookies_path):
        cookies_data = open(cookies_path).read()
    else:
        cookies_data= ""

    return render(request, "downloader/settings.html", context={
        'COOKIES_PATH': cookies_path,
        'PO_TOKEN' : os.getenv('PO_TOKEN'),
        'OUTPUT_DIR': os.getenv('OCTO_OUTPUT_DIR'),
        'cookies_data':cookies_data
    })

def romanize(request):
    if request.method == 'POST':
        lyrics = request.POST.get('lyrics', '')
        romanized = japanese_to_romaji(lyrics)
        return JsonResponse({'romanized': romanized})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def automation_view(request):
    return render(request, 'downloader/automation.html')
```

# octofin/downloader/worker.py

```py
import yt_dlp
import json
import os
from mutagen.oggopus import OggOpus
import base64
import struct
import requests
import shutil
from .utils import crop_to_square_bytes
from .models import DictionaryKey


COOKIES_PATH = os.getenv('COOKIES_PATH')
PO_TOKEN = os.getenv('PO_TOKEN')
OUTPUT_DIR = os.getenv('OCTO_OUTPUT_DIR')


def download_image_bytes(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

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

def getytdata(url:str) -> dict:
    os.makedirs('temp/', exist_ok=True)

    v_id = url.split("?v=")[-1].split("&")[0]
    file = f'temp/{v_id}.json'
    if os.path.exists(file):
        raw_data = json.loads(open(file).read())
        return extract_data(raw_data)

    ydl_opts = {
        'cookiefile': f'{COOKIES_PATH}',
        'extract_flat': 'discard_in_playlist',
        'extractor_args': {
            'youtube': {
                'po_token': [f'web_music.gvs+{PO_TOKEN}']
                }
            },
        }

    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        _info:dict = ydl.extract_info(url, download=False) # type: ignore

    with open(file, 'w') as f:
        f.write(json.dumps(_info, indent=2))

    return extract_data(_info)

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
        temp_file = ydl.prepare_filename(info['a_info']) + '.opus'
        if not os.path.exists(temp_file):
            error_code = ydl.download(info['url'])
            print(error_code)

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

    dest_dir = os.path.join(OUTPUT_DIR, album_artist, f'[{year}] {album}') # type: ignore

    os.makedirs(dest_dir, exist_ok=True)
    filename = os.path.basename(file_path)
    dest_path = os.path.join(dest_dir, filename)
    shutil.move(file_path, dest_path)

    return dest_path
```

# octofin/likedplaylist/__init__.py

```py

```

# octofin/likedplaylist/admin.py

```py
from django.contrib import admin
from .models import JellyfinAccount, AppConfig

@admin.register(JellyfinAccount)
class JellyfinAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'server')

@admin.register(AppConfig)
class AppConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')

```

# octofin/likedplaylist/apps.py

```py
from django.apps import AppConfig


class LikedplaylistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'likedplaylist'

```

# octofin/likedplaylist/forms.py

```py
from django import forms
from .models import JellyfinAccount

class JellyfinAccountForm(forms.ModelForm):
    class Meta:
        model = JellyfinAccount
        fields = ['server', 'username', 'password']
        widgets = {'password': forms.PasswordInput(render_value=True)}

class AccountToggleForm(forms.Form):
    account_id = forms.IntegerField(widget=forms.HiddenInput())
    is_active = forms.BooleanField(required=False)

```

# octofin/likedplaylist/jellyfin.py

```py
import requests
from pathlib import Path
import base64
import time
from django.conf import settings

def get_headers(token=None, content_type=None):
    auth_str = 'MediaBrowser Client="Octo", Device="Chrome", DeviceId="TW96aWxsYS81LjAgKFgxMaHJvbWUvMTMxLjAuMCNjc4NQ11", Version="10.10.3"'
    if token:
        auth_str += f', Token="{token}"'
    
    headers = {'authorization': auth_str}
    if content_type:
        headers['Content-Type'] = content_type
    return headers

def authenticate_account(account):
    auth_url = f"{account.server}/Users/AuthenticateByName"
    payload = {"Username": account.username, "Pw": account.password}
    
    response = requests.post(auth_url, json=payload, headers=get_headers())
    response.raise_for_status()
    
    data = response.json()
    account.token = data["AccessToken"]
    account.user_id = data["User"]["Id"]
    account.save()

def get_playlists(account):
    if not account.token:
        authenticate_account(account)
        
    url = f"{account.server}/Users/{account.user_id}/Items?includeItemTypes=Playlist&Recursive=true"
    response = requests.get(url, headers=get_headers(account.token))
    return {item['Name']: item['Id'] for item in response.json()['Items']}

def create_playlist(account, name):
    url = f"{account.server}/Playlists"
    payload = {"Name": name, "UserId": account.user_id, "isPublic":False}
    response = requests.post(url, json=payload, headers=get_headers(account.token))
    playlist_id = response.json()['Id']
    
    
    # Update description
    
    payload = {"Id":playlist_id,
               "Name":"Liked Songs",
               "OriginalTitle":"Liked Songs",
               "ForcedSortName":"",
               "CommunityRating":"",
               "CriticRating":"",
               "IndexNumber":None,
               "AirsBeforeSeasonNumber":"",
               "AirsAfterSeasonNumber":"",
               "AirsBeforeEpisodeNumber":"",
               "ParentIndexNumber":None,
               "DisplayOrder":"",
               "Album":"","AlbumArtists":[],"ArtistItems":[],
               "Overview":f"{account.username}'s Liked Songs Playlist",
               "Status":"","AirDays":[],"AirTime":"","Genres":[],"Tags":[],"Studios":[],
               "PremiereDate":None,"DateCreated":"1970-01-01T00:01:00.000Z","EndDate":None,
               "ProductionYear":"","Height":"","AspectRatio":"","Video3DFormat":"","OfficialRating":"",
               "CustomRating":"","People":[],"LockData":False,"LockedFields":[],"ProviderIds":{},
               "PreferredMetadataLanguage":"","PreferredMetadataCountryCode":"","Taglines":[]}
    url = f"{account.server}/Items/{playlist_id}"
    response = requests.post(url, json=payload, headers=get_headers(account.token))
    
    return playlist_id

def get_fav_tracks(account):
    url = f"{account.server}/Items?includeItemTypes=Audio&filters=IsFavorite&Recursive=true"
    response = requests.get(url, headers=get_headers(account.token))
    return [item['Id'] for item in response.json()["Items"]]

def get_playlist_tracks(account, playlist_id):
    url = f"{account.server}/Playlists/{playlist_id}/Items"
    response = requests.get(url, headers=get_headers(account.token))
    return [item['Id'] for item in response.json()["Items"]]

def add_items_to_playlist(account, playlist_id, items):
    batch_size = 100
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        ids_str = ",".join(batch)
        url = f"{account.server}/Playlists/{playlist_id}/Items?ids={ids_str}"
        response = requests.post(url, headers=get_headers(account.token))
        time.sleep(0.5)

def remove_item_from_playlist(account, playlist_id, item_id):
    url = f"{account.server}/Playlists/{playlist_id}/Items?EntryIds={item_id}"
    requests.delete(url, headers=get_headers(account.token))

def update_playlist_icon(account, playlist_id, image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    content_type = "image/jpeg" if image_path.endswith(".jpg") else "image/png"
    url = f"{account.server}/Items/{playlist_id}/Images/Primary"
    
    requests.post(
        url,
        headers=get_headers(account.token, content_type),
        data=base64.b64encode(image_data)
    )

def sync_playlist_for_account(account, config):
    if not account.is_active:
        return
    # Authentication
    if not account.token:
        authenticate_account(account)
    
    # Get or create playlist
    playlists = get_playlists(account)
    if "Liked Songs" in playlists:
        account.liked_playlist_id = playlists["Liked Songs"]
    else:
        account.liked_playlist_id = create_playlist(account, "Liked Songs")
        if 'LIKED_SONGS_PLAYLIST_ICON' in config:
            update_playlist_icon(
                account,
                account.liked_playlist_id,
                config['LIKED_SONGS_PLAYLIST_ICON']
            )
    account.save()
    
    # Sync tracks
    fav_tracks = get_fav_tracks(account)
    pl_tracks = get_playlist_tracks(account, account.liked_playlist_id)
    missing = [t for t in fav_tracks if t not in pl_tracks]
    
    if missing:
        add_items_to_playlist(account, account.liked_playlist_id, missing)

```

# octofin/likedplaylist/management/commands/sync_playlists.py

```py
# likedplaylist/management/commands/sync_playlists.py
import sys
from django.core.management.base import BaseCommand
from likedplaylist.models import JellyfinAccount, AppConfig
from likedplaylist.jellyfin import sync_playlist_for_account

class Command(BaseCommand):
    help = 'Syncs liked playlists for all Jellyfin accounts'

    def handle(self, *args, **kwargs):
        config = AppConfig.get_config()
        accounts = JellyfinAccount.objects.all()
        
        for account in accounts:
            # Force flush after each print
            self.stdout.write(f"Processing account: {account.username}", ending='\n')
            self.stdout.flush()
            
            # Add more progress updates
            self.stdout.write(f"Authenticating {account.username}...")
            self.stdout.flush()
            
            sync_playlist_for_account(account, config)
            
            # Add completion message
            self.stdout.write(f"Completed sync for {account.username}", ending='\n')
            self.stdout.flush()

```

# octofin/likedplaylist/models.py

```py
from django.db import models

class JellyfinAccount(models.Model):
    server = models.URLField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    token = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    liked_playlist_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

class AppConfig(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()

    @classmethod
    def get_config(cls):
        return {c.key: c.value for c in cls.objects.all()}

```

# octofin/likedplaylist/tests.py

```py
from django.test import TestCase

# Create your tests here.

```

# octofin/likedplaylist/urls.py

```py
from django.urls import path
from .views import jellyfin_webhook, configView

urlpatterns = [
    path('webhook/', jellyfin_webhook, name='jellyfin-webhook'),
    path('config/', configView, name='likedplaylist-config')
]

```

# octofin/likedplaylist/views.py

```py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JellyfinAccount, AppConfig
from .jellyfin import remove_item_from_playlist, add_items_to_playlist, sync_playlist_for_account
import json
from django.shortcuts import render, redirect
from .forms import JellyfinAccountForm, AccountToggleForm


def configView(request):
    accounts = JellyfinAccount.objects.all()
    account_form = JellyfinAccountForm(request.POST or None)
    toggle_form = AccountToggleForm(request.POST or None)
    
    if request.method == 'POST':
        if 'add_account' in request.POST and account_form.is_valid():
            account_form.save()
            return redirect('likedplaylist-config')
        
        if 'toggle_account' in request.POST and toggle_form.is_valid():
            account_id = toggle_form.cleaned_data['account_id']
            is_active = toggle_form.cleaned_data['is_active']
            account = JellyfinAccount.objects.get(id=account_id)
            account.is_active = is_active
            account.save()
            return redirect('likedplaylist-config')
        
        if 'sync_account' in request.POST:
            account_id = request.POST.get('account_id')
            account = JellyfinAccount.objects.get(id=account_id)
            config = AppConfig.get_config()
            sync_playlist_for_account(account, config)
            return redirect('likedplaylist-config')
        
        if 'sync_all' in request.POST:
            config = AppConfig.get_config()
            for account in accounts.filter(is_active=True):
                sync_playlist_for_account(account, config)
            return redirect('likedplaylist-config')
    
    return render(request, 'likedplaylist/config.html', {
        'accounts': accounts,
        'account_form': account_form,
        'toggle_form': toggle_form
    })

@csrf_exempt
def jellyfin_webhook(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        print(data)
        user_id = data.get('user_id').replace('-','')
        item_id = data.get('item_id').replace('-', '')
        save_reason = data.get('saveReason')
        
        if not all([user_id, item_id, save_reason]):
            return JsonResponse({"error": "Missing parameters"}, status=400)
        
        try:
            account = JellyfinAccount.objects.get(user_id=user_id)
        except JellyfinAccount.DoesNotExist:
            print("Account not found")
            return JsonResponse({"error": "Account not found"}, status=404)
        
        if save_reason == 'Unsave':
            remove_item_from_playlist(account, account.liked_playlist_id, item_id)
        else:  # 'Save'
            add_items_to_playlist(account, account.liked_playlist_id, [item_id])
        
        return JsonResponse({"status": "success"})
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

```

# octofin/manage.py

```py
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'octofin.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

```

# octofin/octofin/__init__.py

```py

```

# octofin/octofin/asgi.py

```py
"""
ASGI config for octofin project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'octofin.settings')

application = get_asgi_application()

```

# octofin/octofin/settings.py

```py
"""
Django settings for octofin project.

Generated by 'django-admin startproject' using Django 5.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-qgz=o9p4xj1z25v&!^0+-o#w(w@d80b@l0^__qf9w+d01l&ov+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'downloader',
    'likedplaylist',
    'playlistman'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'octofin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'downloader.context_processors.footer_version',
                'config.context_processor.global_config'
            ],
        },
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

WSGI_APPLICATION = 'octofin.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'downloader/static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

```

# octofin/octofin/urls.py

```py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('ytm/', include('downloader.urls')),
    path('likedplaylist/', include('likedplaylist.urls')),
    path('playlistman/', include('playlistman.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

# octofin/octofin/wsgi.py

```py
"""
WSGI config for octofin project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'octofin.settings')

application = get_wsgi_application()

```

# octofin/playlistman/__init__.py

```py

```

# octofin/playlistman/admin.py

```py
from django.contrib import admin

# Register your models here.

```

# octofin/playlistman/apps.py

```py
from django.apps import AppConfig


class PlaylistmanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'playlistman'

```

# octofin/playlistman/models.py

```py
from django.db import models

# Create your models here.

```

# octofin/playlistman/tests.py

```py
from django.test import TestCase

# Create your tests here.

```

# octofin/playlistman/urls.py

```py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
]
```

# octofin/playlistman/views.py

```py
from django.shortcuts import render

# Create your views here.
def index_view(request):
    return render(request, 'playlistman/index.html')
```

