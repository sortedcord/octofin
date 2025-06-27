# Octofin

Octofin is a set of tools and scripts that adds QoL functionality to your Jellyfin music library.

## Contents

- [1. YTM Importer](#1-ytm-importer)
- [2. Liked Songs Playlist](#2-liked-songs-playlist)
- [3. Web Configuration](#3-web-configuration)

## 1. YTM Importer

Octofin has a YouTube Music downloader that downloads tracks and adds them to your music library.

![youtube music importer](docs/img/1.png)

### Setup

Use the Docker Compose configuration:

```docker
services:
web:
image: sortedcord/octofin
ports:
- "8193:8193"
  volumes:
- ./path_to_music_library:/music
- ./config:/app/octofin/config_data
  restart: unless-stopped
```

Build and run the container:

```sh
docker-compose up --build
```

The downloader will be accessible at `http://localhost:8193`

## 2. Liked Songs Playlist

Automatically syncs your favorite songs into a virtual playlist. An extended version of [Jellyfin Liked Playlist](https://github.com/Groovbox/jellyfin-liked-playlist) with enhanced management.

## 3. Web Configuration

All settings are now managed through the web interface:

1. Access `http://localhost:8193/config/` after starting
2. Configure:
    - YouTube PO Token
    - Cookies file path
    - Output directory
    - Jellyfin server connection
    - Liked playlist settings

![configuration interface](docs/img/config_screenshot.png)

### Key Features
- **Runtime configuration**: Change settings without restarting
- **Centralized management**: All settings in one place
- **Persistent storage**: Configurations saved across restarts
- **Dark mode support**: Consistent UI experience

### Migrating from .env
Existing `.env` users can:
1. Start Octofin without environment variables
2. Enter settings through the web interface
3. Remove `.env` file after migration