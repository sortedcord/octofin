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
    payload = {"Name": name, "UserId": account.user_id}
    response = requests.post(url, json=payload, headers=get_headers(account.token))
    return response.json()['Id']

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
