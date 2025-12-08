from flask import Flask, render_template, request, jsonify, Response
import requests
import json
from datetime import datetime, timedelta
import re
import base64
import urllib3
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad
import yt_dlp
import traceback
from fuzzywuzzy import fuzz
from http.cookies import SimpleCookie
import tempfile
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ==================== JioSaavn API ====================
class JioSaavnService:
    BASE_URL = 'https://www.jiosaavn.com/api.php'
    
    @staticmethod
    def decode_url(encrypted_url):
        """Decrypt JioSaavn encrypted media URLs"""
        try:
            key = b'38346591'
            cipher = DES.new(key, DES.MODE_ECB)
            encrypted_data = base64.b64decode(encrypted_url)
            decrypted = unpad(cipher.decrypt(encrypted_data), DES.block_size)
            decoded_url = decrypted.decode('utf-8')
            decoded_url = re.sub(r'\.mp4.*', '.mp4', decoded_url)
            decoded_url = re.sub(r'\.m4a.*', '.m4a', decoded_url)
            return decoded_url.replace('http:', 'https:')
        except Exception as e:
            print(f"Decode error: {e}")
            return None
    
    @staticmethod
    def search(query, limit=20):
        try:
            params = {
                '__call': 'autocomplete.get',
                '_format': 'json',
                '_marker': '0',
                'cc': 'in',
                'includeMetaTags': '1',
                'query': query
            }
            
            response = requests.get(JioSaavnService.BASE_URL, params=params, verify=False)
            data = response.json()
            
            results = []
            
            # Process songs
            if 'songs' in data and 'data' in data['songs']:
                for song in data['songs']['data'][:limit]:
                    more_info = song.get('more_info', {})
                    results.append({
                        'id': song.get('id'),
                        'title': song.get('title', ''),
                        'artist': more_info.get('singers', song.get('subtitle', '')),
                        'album': more_info.get('album', ''),
                        'image': song.get('image', '').replace('150x150', '500x500'),
                        'duration': more_info.get('duration', ''),
                        'year': song.get('year', ''),
                        'language': song.get('language', ''),
                        'has_320kbps': more_info.get('320kbps') == 'true',
                        'type': 'song',
                        'provider': 'saavn'
                    })
            
            return results
        
        except Exception as e:
            print(f"JioSaavn search error: {e}")
            return []
    
    @staticmethod
    def get_song_details(song_id):
        """Get detailed song information including encrypted URL"""
        try:
            params = {
                '__call': 'song.getDetails',
                'cc': 'in',
                'pids': song_id,
                '_format': 'json',
                '_marker': '0'
            }
            
            response = requests.get(JioSaavnService.BASE_URL, params=params, verify=False)
            data = response.json()
            
            if isinstance(data, dict) and song_id in data:
                return data[song_id]
            elif isinstance(data, list) and len(data) > 0:
                return data[0]
            
            return None
        
        except Exception as e:
            print(f"JioSaavn details error: {e}")
            return None
    
    @staticmethod
    def get_song_url(song_id):
        """Get streaming URL for a song"""
        try:
            song_details = JioSaavnService.get_song_details(song_id)
            
            if not song_details:
                return None
            
            # Try to get the best quality URL
            more_info = song_details.get('more_info', {})
            encrypted_url = song_details.get('encrypted_media_url', more_info.get('encrypted_media_url'))
            
            if encrypted_url:
                decrypted_url = JioSaavnService.decode_url(encrypted_url)
                if decrypted_url:
                    # Request the highest quality
                    quality_url = decrypted_url.replace('_96.mp4', '_320.mp4').replace('_96.m4a', '_320.m4a')
                    return quality_url
            
            return None
        
        except Exception as e:
            print(f"JioSaavn URL error: {e}")
            return None

# ==================== YouTube Music API ====================
YTM_DOMAIN = 'music.youtube.com'
YTM_PARAMS = {
    'alt': 'json',
    'key': 'AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30'
}
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'

class YtMusicService:
    def __init__(self):
        self.headers = None
        self.context = None
        
    def initialize_headers(self):
        return {
            'user-agent': USER_AGENT,
            'accept': '*/*',
            'content-type': 'application/json',
            'origin': f'https://{YTM_DOMAIN}',
            'cookie': 'CONSENT=YES+1',
            'Accept-Language': 'en',
        }
    
    def initialize_context(self):
        now = datetime.now()
        date = now.strftime('%Y%m%d')
        return {
            'context': {
                'client': {
                    'clientName': 'WEB_REMIX',
                    'clientVersion': f'1.{date}.01.00',
                    'hl': 'en',
                    'gl': 'US',
                },
                'user': {}
            }
        }
    
    def init(self):
        self.headers = self.initialize_headers()
        self.context = self.initialize_context()
    
    def search(self, query, limit=10):
        if not self.headers:
            self.init()
        
        body = dict(self.context)
        body['query'] = query
        body['params'] = 'EgWKAQIIAWoMEA4QChADEAQQCRAF'  # Songs filter
        
        url = f'https://{YTM_DOMAIN}/youtubei/v1/search'
        
        try:
            response = requests.post(url, headers=self.headers, json=body, params=YTM_PARAMS, verify=False)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = self._parse_search_results(data, limit)
            return results
        
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []
    
    def _parse_search_results(self, data, limit=10):
        results = []
        
        try:
            contents = data.get('contents', {})
            tabs = contents.get('tabbedSearchResultsRenderer', {}).get('tabs', [])
            
            if not tabs:
                return []
            
            tab_content = tabs[0].get('tabRenderer', {}).get('content', {})
            sections = tab_content.get('sectionListRenderer', {}).get('contents', [])
            
            for section in sections:
                items = section.get('musicShelfRenderer', {}).get('contents', [])
                
                for item in items:
                    if len(results) >= limit:
                        break
                        
                    try:
                        renderer = item.get('musicResponsiveListItemRenderer', {})
                        
                        # Get video ID
                        video_id = renderer.get('playlistItemData', {}).get('videoId')
                        if not video_id:
                            continue
                        
                        # Get title
                        title_runs = renderer.get('flexColumns', [{}])[0].get(
                            'musicResponsiveListItemFlexColumnRenderer', {}
                        ).get('text', {}).get('runs', [])
                        title = title_runs[0].get('text', '') if title_runs else ''
                        
                        # Get artists and album
                        subtitle_runs = []
                        if len(renderer.get('flexColumns', [])) > 1:
                            subtitle_runs = renderer.get('flexColumns', [])[1].get(
                                'musicResponsiveListItemFlexColumnRenderer', {}
                            ).get('text', {}).get('runs', [])
                        
                        artists = []
                        album = ''
                        duration = ''
                        
                        for run in subtitle_runs:
                            text = run.get('text', '')
                            endpoint = run.get('navigationEndpoint', {}).get('browseEndpoint', {})
                            page_type = endpoint.get('browseEndpointContextSupportedConfigs', {}).get(
                                'browseEndpointContextMusicConfig', {}
                            ).get('pageType', '')
                            
                            if page_type == 'MUSIC_PAGE_TYPE_ARTIST':
                                artists.append(text)
                            elif page_type == 'MUSIC_PAGE_TYPE_ALBUM':
                                album = text
                            elif ':' in text and text.replace(':', '').replace(' ', '').isdigit():
                                parts = text.split(':')
                                if len(parts) == 2:
                                    duration = str(int(parts[0]) * 60 + int(parts[1]))
                        
                        # Get thumbnail
                        thumbnails = renderer.get('thumbnail', {}).get(
                            'musicThumbnailRenderer', {}
                        ).get('thumbnail', {}).get('thumbnails', [])
                        image = thumbnails[0].get('url', '') if thumbnails else ''
                        image = image.replace('w60-h60', 'w500-h500')
                        
                        results.append({
                            'id': video_id,
                            'title': title,
                            'artist': ', '.join(artists),
                            'album': album,
                            'image': image,
                            'duration': duration,
                            'type': 'song',
                            'provider': 'youtube'
                        })
                    
                    except Exception as e:
                        print(f"Error parsing item: {e}")
                        continue
        
        except Exception as e:
            print(f"Error parsing search results: {e}")
        
        return results

ytm_service = YtMusicService()

# ==================== YouTube Audio Extraction ====================
def get_youtube_audio_url(video_id):
    """Extract direct audio URL from YouTube using yt-dlp"""
    try:
        print(f"Extracting audio URL for YouTube video: {video_id}")
        
        # Generate dynamic cookies using SimpleCookie
        import random
        import string
        
        cookie = SimpleCookie()
        
        # Generate realistic cookie values
        visitor_id = ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=22))
        pref_value = f'tz=America.New_York&f6={random.randint(10000, 99999)}&f5={random.randint(20000, 29999)}'
        
        cookie['VISITOR_INFO1_LIVE'] = visitor_id
        cookie['VISITOR_INFO1_LIVE']['domain'] = '.youtube.com'
        cookie['VISITOR_INFO1_LIVE']['path'] = '/'
        
        cookie['PREF'] = pref_value
        cookie['PREF']['domain'] = '.youtube.com'
        cookie['PREF']['path'] = '/'
        
        cookie['CONSENT'] = f'YES+cb.20210328-17-p0.en+FX+{random.randint(100, 999)}'
        cookie['CONSENT']['domain'] = '.youtube.com'
        cookie['CONSENT']['path'] = '/'
        
        # Create temporary cookie file
        cookie_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        cookie_file.write('# Netscape HTTP Cookie File\n')
        cookie_file.write('# This is a generated file! Do not edit.\n\n')
        
        for key in cookie:
            domain = cookie[key].get('domain', '.youtube.com')
            path = cookie[key].get('path', '/')
            secure = 'TRUE'
            expires = '2147483647'  # Year 2038
            name = key
            value = cookie[key].value
            cookie_file.write(f'{domain}\tTRUE\t{path}\t{secure}\t{expires}\t{name}\t{value}\n')
        
        cookie_file.close()
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'socket_timeout': 30,
                'http_chunk_size': 10485760,
                'extractor_retries': 3,
                'retries': 3,
                'cookiefile': cookie_file.name,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'skip': ['hls', 'dash', 'translated_subs']
                    }
                }
            }
            
            url = f'https://www.youtube.com/watch?v={video_id}'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Try to get the best audio format URL directly
                if 'url' in info:
                    print(f"Found direct audio URL")
                    return info['url']
                
                # Try to get the best audio format
                if 'formats' in info:
                    # Filter audio-only formats
                    audio_formats = [f for f in info['formats'] 
                                   if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                    
                    if audio_formats:
                        # Sort by audio bitrate and get the best
                        best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
                        audio_url = best_audio.get('url')
                        print(f"Found best audio format: {best_audio.get('format_note', 'unknown')} - {best_audio.get('abr', 0)}kbps")
                        return audio_url
                    
                    # Fallback: get any format with audio
                    for fmt in info['formats']:
                        if fmt.get('acodec') != 'none' and fmt.get('url'):
                            print(f"Using fallback format: {fmt.get('format_note', 'unknown')}")
                            return fmt['url']
                
                print("No audio URL found")
                return None
        finally:
            # Clean up cookie file
            try:
                os.unlink(cookie_file.name)
            except:
                pass
    
    except Exception as e:
        print(f"Error extracting YouTube audio: {e}")
        traceback.print_exc()
        return None

# ==================== Mixed API ====================
class MixedAPI:
    """Smart API that searches both JioSaavn and YouTube Music and returns best match"""
    
    @staticmethod
    def select_best_match(query, saavn_result, yt_result):
        """Compare search results and select the best match using fuzzy string matching"""
        # Create comparison strings
        saavn_str = f"{saavn_result['title']} {saavn_result['artist']}".lower().strip()
        yt_str = f"{yt_result['title']} {yt_result['artist']}".lower().strip()
        query_lower = query.lower().strip()
        
        # Calculate similarity scores
        saavn_ratio = fuzz.ratio(query_lower, saavn_str)
        saavn_partial = fuzz.partial_ratio(query_lower, saavn_str)
        
        yt_ratio = fuzz.ratio(query_lower, yt_str)
        yt_partial = fuzz.partial_ratio(query_lower, yt_str)
        
        # Use best score for each provider
        saavn_score = max(saavn_ratio, saavn_partial)
        yt_score = max(yt_ratio, yt_partial)
        
        print(f"MixedAPI - JioSaavn: '{saavn_str}' score={saavn_score}, YouTube: '{yt_str}' score={yt_score}")
        
        # Return the better match
        if saavn_score >= yt_score:
            print(f"Selected JioSaavn result (score: {saavn_score})")
            return saavn_result
        else:
            print(f"Selected YouTube result (score: {yt_score})")
            return yt_result
    
    @staticmethod
    def search_mixed(query, limit=10):
        """Search both providers and return intelligently merged results"""
        print(f"MixedAPI searching: {query}")
        
        # Search both providers
        saavn_results = JioSaavnService.search(query, limit=limit)
        yt_results = ytm_service.search(query, limit=limit)
        
        if not saavn_results and not yt_results:
            return []
        
        if not saavn_results:
            print("Only YouTube results available")
            return yt_results
        
        if not yt_results:
            print("Only JioSaavn results available")
            return saavn_results
        
        # Match results from both providers and select best
        merged_results = []
        used_saavn_ids = set()
        used_yt_ids = set()
        
        # For each JioSaavn result, try to find matching YouTube result
        for saavn_item in saavn_results:
            best_match = None
            best_score = 80  # Minimum confidence threshold
            
            saavn_str = f"{saavn_item['title']} {saavn_item['artist']}".lower().strip()
            
            for yt_item in yt_results:
                if yt_item['id'] in used_yt_ids:
                    continue
                
                yt_str = f"{yt_item['title']} {yt_item['artist']}".lower().strip()
                
                # Check if they're the same song
                ratio = fuzz.ratio(saavn_str, yt_str)
                partial = fuzz.partial_ratio(saavn_str, yt_str)
                score = max(ratio, partial)
                
                if score > best_score:
                    best_score = score
                    best_match = yt_item
            
            if best_match:
                # Found a match - select the better one
                selected = MixedAPI.select_best_match(query, saavn_item, best_match)
                merged_results.append(selected)
                used_saavn_ids.add(saavn_item['id'])
                used_yt_ids.add(best_match['id'])
            else:
                # No match found, add JioSaavn result
                merged_results.append(saavn_item)
                used_saavn_ids.add(saavn_item['id'])
        
        # Add remaining YouTube results that weren't matched
        for yt_item in yt_results:
            if yt_item['id'] not in used_yt_ids:
                merged_results.append(yt_item)
        
        print(f"MixedAPI returned {len(merged_results)} results")
        return merged_results[:limit]

# ==================== Initialize Services ====================
ytm_service = YtMusicService()

# ==================== Routes ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/providers')
def get_providers():
    """Get list of available music providers"""
    return jsonify({
        'providers': [
            {'id': 'mixed', 'name': 'Smart Mix (Best Results)', 'enabled': True},
            {'id': 'saavn', 'name': 'JioSaavn', 'enabled': True},
            {'id': 'youtube', 'name': 'YouTube Music', 'enabled': True},
            {'id': 'all', 'name': 'All Providers', 'enabled': True}
        ]
    })

@app.route('/search')
def search():
    query = request.args.get('q', '')
    provider = request.args.get('provider', 'all')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    print(f"Searching '{query}' on provider: {provider}")
    
    all_results = []
    
    try:
        if provider == 'mixed':
            # Use intelligent mixed search
            all_results = MixedAPI.search_mixed(query)
        elif provider == 'all':
            # Return all results from both providers
            saavn_results = JioSaavnService.search(query)
            all_results.extend(saavn_results)
            
            ytm_results = ytm_service.search(query)
            all_results.extend(ytm_results)
        elif provider == 'saavn':
            all_results = JioSaavnService.search(query)
        elif provider == 'youtube':
            all_results = ytm_service.search(query)
        
        return jsonify(all_results)
    
    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/stream')
def stream():
    song_id = request.args.get('id', '')
    provider = request.args.get('provider', 'saavn')
    
    if not song_id:
        return jsonify({'error': 'No ID provided'}), 400
    
    print(f"Stream request for ID: {song_id}, provider: {provider}")
    
    try:
        stream_url = None
        
        if provider == 'saavn':
            stream_url = JioSaavnService.get_song_url(song_id)
        elif provider == 'youtube':
            # Use yt-dlp to extract direct audio URL
            stream_url = get_youtube_audio_url(song_id)
        
        if stream_url:
            print(f"Successfully got stream URL from {provider}: {stream_url[:80]}...")
            return jsonify({'url': stream_url, 'provider': provider})
        else:
            print(f"Failed to get stream URL from {provider}")
            return jsonify({'error': f'Could not get stream URL from {provider}'}), 500
    
    except Exception as e:
        print(f"Error in stream endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
