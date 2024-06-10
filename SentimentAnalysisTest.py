from deepmultilingualpunctuation import PunctuationModel
import nltk
import json
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('stopwords')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from vectorSpaceModel import get_mean_cosine_similarity
from vectorSpaceModel import get_data_from_CSV
from vectorSpaceModel import create_dict

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

def get_sentiment_from_text(raw_text):
   sentiment = 0
   if (len(raw_text) > 0):
      text = prep_text(raw_text)
      text_len = len(text)
      transcript_sentiment = sentiment_analysis(text)/text_len
      sentiment = transcript_sentiment
   return sentiment

def main():
   f = open("transcripts.json")
   raw = json.load(f)
   f.close()
   res = {}
   data_csv, ids = get_data_from_CSV(True)
   dict_nlp = create_dict(data_csv)
   
   for country_transcripts in raw:
      for country, data in country_transcripts.items():
         res[country] = {}
         sentiment = 0
         comment_sentiment = 0
         country_sentiment_comment = 0
         cosine_similarity = 0.0
         cosine_similarity_comments = 0.0
         for video in data:
            tmp_comments_cosine_similarity = 0.0
            transcript = video['transcript']
            sentiment += get_sentiment_from_text(transcript)
            cosine_similarity += get_mean_cosine_similarity(transcript, dict_nlp, ids)
            for comment in video['comments']:
               comment_sentiment += get_sentiment_from_text(comment)
               tmp_comments_cosine_similarity += get_mean_cosine_similarity(comment, dict_nlp, ids)
            if (len(video['comments']) > 0):
               country_sentiment_comment = comment_sentiment/len(video['comments'])
               tmp_comments_cosine_similarity = tmp_comments_cosine_similarity/len(video['comments'])
            cosine_similarity_comments += tmp_comments_cosine_similarity

         country_sentiment = sentiment/len(data)
         country_cosine_similarity = cosine_similarity/len(data)
         cosine_similarity_comments = cosine_similarity_comments/len(data)
         res[country]["sentiment"] = country_sentiment
         res[country]["comments_sentiment"] = country_sentiment_comment
         res[country]["cosine_similarity"] = country_cosine_similarity
         res[country]["cosine_similarity_comments"] = cosine_similarity_comments
         print("\n")
         print(f"Sentiment analysis result for {country}'s videos:", country_sentiment)
         print(f"Mean Sentiment analysis result for {country}'s comments:", country_sentiment_comment)
         print(f"Mean Cosine Similarity for {country}'s videos:", country_cosine_similarity)
         print(f"Mean Cosine Similarity for {country}'s comments:", cosine_similarity_comments)
         if country_sentiment > 0.05:
            print(f"{country}'s videos sentiments are positive")
         elif 0.05 >= country_sentiment >= -0.05:
            print(f"{country}'s videos sentiments are neutral")
         else:
            print(f"{country}'s videos sentiments are negative")
         if country_sentiment_comment > 0.05:
            print(f"{country}'s comments sentiments are positive")
         elif 0.05 >= country_sentiment_comment >= -0.05:
            print(f"{country}'s comments sentiments are neutral")
         else:
            print(f"{country}'s comments sentiments are negative")

   res_json = "results.json"
   with open(res_json, 'w') as json_file:
      json.dump(res, json_file, indent=2)

main()