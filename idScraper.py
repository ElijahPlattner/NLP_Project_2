from googleapiclient.discovery import build
import json

api_key = 'AIzaSyDgWWxgNb_2-x5stWsI14xUujW8qIYP_n4'

youtube = build('youtube', 'v3', developerKey=api_key)

nextPageToken = ""
videos = []
for page in range(5):
    request = youtube.search().list(
        part="snippet",
        q="lgbq",
        type="video",
        location = "39.466354,-106.210162",
        locationRadius = "1000km",
        relevanceLanguage = "en",
        videoDuration="medium",
        publishedAfter="2024-03-25T00:00:00Z",
        maxResults=50,
        pageToken=nextPageToken
    )

    response = request.execute()

    if page != 1:
        nextPageToken = response['nextPageToken']

    if 'items' in response:
        for item in response['items']:
            video = {
                'id': item['id']['videoId']
            }
            videos.append(video)
            print(video)

    print(str(page) + "...")
print(videos)

# Save the data to a new JSON file
json_file_path = 'west_usa'
with open(json_file_path, 'w') as json_file:
    json.dump(videos, json_file, indent=2)

print("JSON file done!")
