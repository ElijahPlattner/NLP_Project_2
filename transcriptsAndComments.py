from youtube_transcript_api import YouTubeTranscriptApi
from deepmultilingualpunctuation import PunctuationModel
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import json
from googleapiclient.discovery import build
import requests
import time
import deepl
model = PunctuationModel()

DEEPL_API_KEY = 'a492ab27-f349-4022-b36e-5535e251c7f0:fx'
translator = deepl.Translator(DEEPL_API_KEY)

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

def get_comments(video_id, api_key, max_results):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=max_results
    )
    comments = []

    try:
        response = request.execute()

        while request:
            response = request.execute()
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)
                if len(comments) >= max_results:
                    break 

            if 'nextPageToken' in response and len(comments) < max_results:
                request = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    pageToken=response['nextPageToken'],
                    maxResults=max_results - len(comments)
                )
            else:
                break

    except Exception as e:
        print(f"An error occurred: {e}")
        comments = [""]

    return comments

def translate_comment(comment, target_lang="EN-US"):
    try:
        result = translator.translate_text(comment, target_lang=target_lang)
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return comment

api_key = 'AIzaSyDgWWxgNb_2-x5stWsI14xUujW8qIYP_n4'

for country_data in raw:
    for country, videos in country_data.items():
        print(country)
        transcripts = []
        for video in videos:
            id = video['id']
            print(id)
            transcript = ""
            try:
                transcript = get_transcript(id)
            except TranscriptsDisabled:
                print(f"Transcripts are disabled for the video with ID {id}.")
            except NoTranscriptFound:
                print(f"No transcript found for the video with ID {id}.")

            comments = get_comments(id, api_key, max_results=10)
            translated_comments = [translate_comment(comment) for comment in comments]

            transcript_data = {
                "id": id,
                "transcript": transcript,
                "comments": translated_comments
            }
            transcripts.append(transcript_data)
            time.sleep(5)

        country_videos = {country: transcripts}
        all_transcripts.append(country_videos)


json_file_path = 'transcripts.json'
with open(json_file_path, 'w') as json_file:
    json.dump(all_transcripts, json_file, indent=2)
