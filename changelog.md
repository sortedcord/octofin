# Changelog 

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1b] - 2025-06-27
### Added
- [ ] Support for album and playlists 
  - [ ] Playlist matching
  - [ ] Playlist creation
- Dynamic Dark Mode Support
- [ ] Error reporting for downloader

### Changed
- Use context processing for footer version
- Changelog formatting on homescreen
- [ ] Refactor settings to app config
- Separated static js from html templates
- Design update

### Fixed
- [ ] DB error for likedplaylist app
- [ ] Format error for release date causing failed download

## [0.0.1a] - 2025-06-25
### Added
- Support for non-tracks (videos) on YouTube music.
- Non-track video thumbnails get auto cropped to 1:1 ratio.
- Add lyrics
- Romanize titles, lyrics
- Rudimentary dictionary support. Automatic word replacement in metadata fields.
- Changelog on home screen

### Changed


### Fixed
- Title not updating when showing up in the process list after editing metadata.
- Updated Queue Status URL
- Removed leading slashes for hyperlinks
- Changelog location error for docker installs
