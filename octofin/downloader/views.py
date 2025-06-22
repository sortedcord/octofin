from django.shortcuts import render, redirect, get_object_or_404
from .worker import getytdata, download_song, apply_metadata, import_song
from .models import DownloadTask
import threading
import os
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages



def home(request):
    tasks = DownloadTask.objects.all().order_by('-created_at')
    return render(request, "downloader/index.html", {'tasks': tasks})

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
        raise e
        task.status = 'failed'
        task.error = str(e) # type: ignore
        task.save()


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
                'release_date': request.POST.get('release_date')
            }
            
            for key, value in edited_data.items():
                task.metadata[key] = value # type: ignore
            
            # Start download in background
            task.status = 'downloading'
            task.save()
            threading.Thread(target=process_download, args=(task.id,)).start() # type: ignore
            
            return redirect('home')
    
    # Use edited metadata if available, else use fetched metadata
    context = task.metadata
    context['task_id'] = task_id
    return render(request, 'downloader/edit.html', context)
        

def process_download(task_id):
    task = DownloadTask.objects.get(id=task_id)
    try:
        # Use edited metadata if available
        info = task.metadata
                
        # Download and process
        file_path = download_song(info) + ".opus" # type: ignore
        apply_metadata(file_path, info)
        import_song(file_path, info)
        
        task.status = 'completed'
        task.save()
    except Exception as e:
        raise e
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
    COOKIES_PATH:str = os.getenv('COOKIES_PATH')
    
    cookies_data = open(COOKIES_PATH).read()
    
    return render(request, "downloader/settings.html", context={
        'COOKIES_PATH': COOKIES_PATH, 
        'PO_TOKEN' : os.getenv('PO_TOKEN'),
        'OUTPUT_DIR': os.getenv('OCTO_OUTPUT_DIR'),
        'cookies_data':cookies_data
    })
