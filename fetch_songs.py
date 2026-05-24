import sys
import os
import json
import urllib.request
import urllib.parse
import re
import random

API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('YOUTUBE_API_KEY')

if not API_KEY:
    print("Please provide a YouTube API key as an argument or set YOUTUBE_API_KEY environment variable.")
    sys.exit(1)
BANDS = [
    { 'name': 'Goose', 'query': 'Goose band official video', 'channelId': 'UCNMe_yeW_kCrjRImbUiQ3ZA' },
    { 'name': 'Geese', 'query': 'Geese band official video', 'channelId': 'UCY1iN9fT5gG7sG3oAAkkQtQ' }
]
MAX_RESULTS = 50 # Fetch more to allow for filtering



def parse_duration(duration_str):
    """Parses ISO 8601 duration (e.g., PT4M13S) into seconds."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def get_video_details(video_ids, api_key):
    """Fetches content details (duration) for a list of video IDs."""
    if not video_ids:
        return {}
        
    ids_str = ",".join(video_ids)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={ids_str}&key={api_key}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            parsed = json.loads(data)
            
            details = {}
            for item in parsed.get('items', []):
                duration_sec = parse_duration(item['contentDetails']['duration'])
                details[item['id']] = duration_sec
            return details
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return {}

def search_youtube_page(query, api_key, channel_id=None, page_token=None):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={encoded_query}&type=video&maxResults=50&key={api_key}"
    if channel_id:
        url += f"&channelId={channel_id}"
    if page_token:
        url += f"&pageToken={page_token}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return {}

def is_valid_video(item, band_name):
    """Checks if a video item passes filtering criteria for a specific band."""
    title = item['snippet']['title'].lower()
    other_band = 'geese' if band_name.lower() == 'goose' else 'goose'

    # Stricter filtering for "official" feel, but allow some live if high quality
    excluded_keywords = [
        'interview', 'review', 'reaction', 'podcast', 'band or sham',
        'geesefest', 'episode', 'out now', 'out next week', 'is out'
    ]
    if any(keyword in title for keyword in excluded_keywords):
        return False

    if any(keyword in title for keyword in ['teaser', 'trailer', 'full album']):
        return False

    # Skip random covers by others
    if 'cover' in title and band_name.lower() not in title:
        return False

    # Avoid cross-contamination
    if other_band in title:
        return False

    return True

def main():
    all_songs = []
    
    for band in BANDS:
        print(f"Fetching songs for {band['name']}...")
        songs_added = 0
        next_page_token = None
        
        while songs_added < 200: # Try to find up to 200 songs
            try:
                response = search_youtube_page(band['query'], API_KEY, band.get('channelId'), next_page_token)
                items = response.get('items', [])
                next_page_token = response.get('nextPageToken')
                
                if not items:
                    break
                
                # Filter out obvious live versions, interviews, and wrong band
                filtered_items = [item for item in items if is_valid_video(item, band['name'])]
                
                if not filtered_items:
                    if not next_page_token:
                        break
                    continue

                # Get video IDs to fetch details
                video_ids = [item['id']['videoId'] for item in filtered_items]
                video_details = get_video_details(video_ids, API_KEY)
                
                for item in filtered_items:
                    video_id = item['id']['videoId']
                    duration = video_details.get(video_id, 0)
                    
                    # Skip if duration is too short (e.g. < 30s) or missing
                    if duration < 30:
                        continue
                        
                    # Calculate random start time
                    # Ensure we have at least 15s of play time
                    max_start = max(0, duration - 20) 
                    start_time = random.randint(0, max_start)
                    
                    song = {
                        'id': f"{band['name'].lower()}-{video_id}",
                        'artist': band['name'],
                        'title': item['snippet']['title'],
                        'youtubeId': video_id,
                        'startTime': start_time,
                        'duration': 15,
                        'totalDuration': duration
                    }
                    all_songs.append(song)
                    songs_added += 1
                    
                    if songs_added >= 200:
                        break
                
                print(f"  Fetched page. Total so far: {songs_added}")
                
                if not next_page_token:
                    break
                    
            except Exception as e:
                print(f"Error fetching for {band['name']}: {e}")
                break
        
        print(f"Finished {band['name']}: Found {songs_added} songs")

    with open('new_songs.json', 'w') as f:
        json.dump(all_songs, f, indent=2)
    print('Saved songs to new_songs.json')

if __name__ == "__main__":
    main()
