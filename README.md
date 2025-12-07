# Multi-Provider Music Player

A Flask-based web application that allows you to search and play music from multiple providers including **JioSaavn** and **YouTube Music**.

## Features

- 🎵 **Multi-Provider Search**: Search across JioSaavn and YouTube Music simultaneously
- 🎧 **Direct Playback**: Play JioSaavn songs directly in the browser
- 🎨 **Beautiful UI**: Modern gradient design with responsive layout
- 🔍 **Provider Selection**: Choose to search from specific providers or all at once
- 📱 **Mobile Friendly**: Works on all devices

## Supported Providers

1. **JioSaavn** - Full playback support with 320kbps quality
2. **YouTube Music** - Search and metadata (opens in YouTube for playback)
3. **All Providers** - Search across all providers simultaneously

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:8080
```

3. Select a provider (or "All Providers" to search everywhere)
4. Search for your favorite songs
5. Click on a song to play it!

## How It Works

### JioSaavn Integration
- Uses the JioSaavn public API to search for songs
- Decrypts encrypted media URLs using DES encryption
- Provides direct 320kbps audio streaming

### YouTube Music Integration
- Implements the YouTube Music unofficial API
- Searches for songs with metadata (title, artist, album, duration)
- Returns YouTube URLs for playback

### API Endpoints

- `GET /` - Main page
- `GET /providers` - Get list of available providers
- `GET /search?q=<query>&provider=<provider>` - Search for content
  - Providers: `all`, `saavn`, `youtube`
- `GET /stream?id=<song_id>&provider=<provider>` - Get streaming URL

## Technologies Used

- **Backend**: Flask (Python)
- **JioSaavn API**: Public API with DES decryption for media URLs
- **YouTube Music API**: Unofficial API implementation
- **Encryption**: PyCryptodome for DES decryption
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with gradient design

## Features Breakdown

### Search Results
- Shows results from selected provider(s)
- Displays song title, artist, album, and duration
- Color-coded badges for each provider
- High-quality album artwork

### Audio Player
- Built-in HTML5 audio player for JioSaavn tracks
- Progress bar with time display
- Album artwork display
- Current track information

### Provider-Specific Behavior

**JioSaavn:**
- Direct streaming in browser
- 320kbps quality support
- Full playback controls

**YouTube Music:**
- Opens in YouTube for playback
- Full metadata available
- Search integration

## Notes

- JioSaavn tracks play directly in the browser
- YouTube Music tracks open in YouTube due to DRM restrictions
- SSL verification is disabled for API requests (corporate proxy compatibility)
- The app uses development server - not for production use

## Credits

Based on the Dart implementations from the YtMusic project, adapted for Flask/Python.

## License

This project is for educational purposes only. Respect the terms of service of the music providers.
