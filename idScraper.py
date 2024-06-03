from googleapiclient.discovery import build
import json

api_key = 'AIzaSyDgWWxgNb_2-x5stWsI14xUujW8qIYP_n4'

youtube = build('youtube', 'v3', developerKey=api_key)

countries_info = {
    'France': {'query': "mariage homosexuel",'location': "46.8115,1.6862", 'locationRadius': "550km", 'relevanceLanguage': "fr"},
    'Korea': {'query': "동성결혼",'location': "36.3504,127.3845", 'locationRadius': "260km", 'relevanceLanguage': "ko"},
    'Japan': {'query': "同性愛者の結婚",'location': "36.099059,138.778529", 'locationRadius': "1000km", 'relevanceLanguage': "ja"},
    'Germany': {'query': "homosexuelle Ehe",'location': "50.9787,11.0328", 'locationRadius': "400km", 'relevanceLanguage': "de"},
    'USA East Coast': {'query': "homosexual marriage",'location': "38.9072,-77.0369", 'locationRadius': "1000km", 'relevanceLanguage': "en"},
    'USA West Coast': {'query': "homosexual marriage",'location': "37.7749,-122.4194", 'locationRadius': "1000km", 'relevanceLanguage': "en"},
    'Poland' : {'query': "małżeństwa homoseksualne",'location': "52.0024862,19.2765179", 'locationRadius': "400km", 'relevanceLanguage': "pl"},
    'Norway': {'query': "homofilt ekteskap",'location': "62.0736,9.1220", 'locationRadius': "500km", 'relevanceLanguage': "no"}
}

all_videos = []

for country, info in countries_info.items():
    nextPageToken = None
    videos = []
    print(f"Processing {country}...")
    request = youtube.search().list(
        part="snippet",
        q=info['query'],
        type="video",
        # location=info['location'],
        # locationRadius=info['locationRadius'],
        relevanceLanguage=info['relevanceLanguage'],
        videoDuration="medium",
        publishedAfter="2020-01-01T00:00:00Z",
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

json_file_path = 'videos_ID_country1.json'
with open(json_file_path, 'w') as json_file:
    json.dump(all_videos, json_file, indent=2)

print("JSON file with all countries' videos done!")