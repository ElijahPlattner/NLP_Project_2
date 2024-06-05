from youtube_transcript_api import YouTubeTranscriptApi
from deepmultilingualpunctuation import PunctuationModel
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import json
from googleapiclient.discovery import build
import requests
model = PunctuationModel()

f = open("sample_videos.json")
raw = json.load(f)
f.close()
all_transcripts = []

def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_transcript(['fr', 'ko', 'ja','de','en','pl','no'])
    transcript_translated = transcript.translate('en')
    trans = transcript_translated.fetch()
    text = ' '.join([str(line['text']) for line in trans])
    result = model.restore_punctuation(text)
    return result


def get_comments(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100
    )

    response = request.execute()

    comments = []

    while request:
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=100
            )
        else:
            break

    return comments


api_key = 'AIzaSyDgWWxgNb_2-x5stWsI14xUujW8qIYP_n4'

for country_data in raw:
    transcripts = []
    for country, videos in country_data.items():
        print(country)
        for video in videos:
            comments = []
            id = video['id']
            print(id)
            try:
                transcript = get_transcript(id)
                comments = get_comments(id, api_key)
                transcript_data = {transcript:comments}
                transcripts.append(transcript_data)
            except TranscriptsDisabled:
                print(f"Transcripts are disabled for the video with ID {id}.")
            except NoTranscriptFound:
                print(f"No transcript found for the video with ID {id}.")

        country_videos = {country: transcripts}
        all_transcripts.append(country_videos)

json_file_path = 'transcripts.json'
with open(json_file_path, 'w') as json_file:
    json.dump(all_transcripts, json_file, indent=2)