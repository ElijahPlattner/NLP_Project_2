from youtube_transcript_api import YouTubeTranscriptApi
from deepmultilingualpunctuation import PunctuationModel
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('stopwords')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

sid = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))
model = PunctuationModel()

def remove_stopwords(text):
   stop_words = set(stopwords.words('english'))
   word_tokens = word_tokenize(text)
   filtered = [w for w in word_tokens if not w.lower() in stop_words]
   clean_text = ' '.join(filtered)
   return clean_text

def prep_text(video_id):
   try:
      transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
      transcript = transcript_list.find_transcript(['fr'])
      transcript_translated = transcript.translate('en')
      trans = transcript_translated.fetch()
      text = ' '.join([str(line['text']) for line in trans])
      result = model.restore_punctuation(text)
      clean_text = remove_stopwords(result)
      sent_text = nltk.sent_tokenize(clean_text)
      return sent_text
   except :
      print(f"Error: Transcript for {video_id} not found.")
      return []


def sentiment_analysis(text):
   sum_score = sum(sid.polarity_scores(sent)['compound'] for sent in text)
   return sum_score


def main():
   text = prep_text("9Hv0V2nMprY")
   sentiment = sentiment_analysis(text)
   n = len(text)
   avg = sentiment / n if n > 0 else 0
   print("Sentiment analysis result:", avg)
   if avg > 0.05:
      print("This video's sentiments are positive")
   elif 0.05 >= avg >= -0.05:
      print("This video's sentiments are neutral")
   else:
      print("This video's sentiments are negative")

main()