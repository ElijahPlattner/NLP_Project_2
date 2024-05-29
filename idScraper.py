from googleapiclient.discovery import build
import json

api_key = 'AIzaSyDgWWxgNb_2-x5stWsI14xUujW8qIYP_n4'

youtube = build('youtube', 'v3', developerKey=api_key)

countries_info = {
    'France': {'location': "46.8115,1.6862", 'locationRadius': "1000km", 'relevanceLanguage': "fr"},
    'Korea': {'location': "36.3504,127.3845", 'locationRadius': "1000km", 'relevanceLanguage': "ko"},
    'Japan': {'location': "35.1815,136.9066", 'locationRadius': "1000km", 'relevanceLanguage': "ja"},
    'Norway': {'location': "62.0736,9.1220", 'locationRadius': "1000km", 'relevanceLanguage': "no"},
    'Germany': {'location': "50.9787,11.0328", 'locationRadius': "1000km", 'relevanceLanguage': "de"},
    'USA East Coast': {'location': "38.9072,-77.0369", 'locationRadius': "1000km", 'relevanceLanguage': "en"},
    'USA West Coast': {'location': "37.7749,-122.4194", 'locationRadius': "1000km", 'relevanceLanguage': "en"}
}

all_videos = []

for country, info in countries_info.items():
    nextPageToken = None
    videos = []
    print(f"Processing {country}...")
    request = youtube.search().list(
        part="snippet",
        q="lgbtq",
        type="video",
        location=info['location'],
        locationRadius=info['locationRadius'],
        relevanceLanguage=info['relevanceLanguage'],
        videoDuration="medium",
        publishedAfter="2024-03-25T00:00:00Z",
        maxResults=50,
        pageToken=nextPageToken
    )
    response = request.execute()

    if 'items' in response:
        for item in response['items']:
            video = {'id': item['id']['videoId']}
            videos.append(video)
    else:
        print(f"No videos found for {country}")

    country_videos = {country: videos}
    all_videos.append(country_videos)

json_file_path = 'videos_ID_country.json'
with open(json_file_path, 'w') as json_file:
    json.dump(all_videos, json_file, indent=2)

print("JSON file with all countries' videos done!")