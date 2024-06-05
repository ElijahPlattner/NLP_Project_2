from deepmultilingualpunctuation import PunctuationModel
import nltk
import json
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

def prep_text(transcript):
   clean_text = remove_stopwords(transcript)
   sent_text = nltk.sent_tokenize(clean_text)
   return sent_text


def sentiment_analysis(text):
   sum_score = sum(sid.polarity_scores(sent)['compound'] for sent in text)
   return sum_score


def main():
   f = open("transcripts.json")
   raw = json.load(f)
   f.close()

   for country_transcripts in raw:
      for country, transcripts in country_transcripts.items():
         sentiment = 0
         print(country)
         for transcript in transcripts:
            text = prep_text(transcript)
            text_len = len(text)
            transcript_sentiment = sentiment_analysis(text)/text_len
            sentiment += transcript_sentiment

         country_sentiment = sentiment/len(transcripts)
         print(f"Sentiment analysis result for {country}:", country_sentiment)
         if country_sentiment > 0.05:
            print(f"{country}'s sentiments are positive")
         elif 0.05 >= country >= -0.05:
            print(f"{country}'s sentiments are neutral")
         else:
            print(f"{country}'s sentiments are negative")

main()