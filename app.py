import nltk
from textblob import TextBlob
import urllib3
from bs4 import BeautifulSoup

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def index():
  return 'Hello World!'

@app.route('/hello')
def hello():
  return 'Hello, greetings from different endpoint'

class CannotProcessURL(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(CannotProcessURL)
def api_error_handler(error):
  response = jsonify(error.to_dict())
  response.status_code = error.status_code
  return response


def get_text_analysis(text):
  # Get the sentences from body
  sentences = text.split(".")

  # Generate the Response
  response = {}
  response["source"] = text
  response["sentences"] = []
  response["sentencecount"] = 0
  response["sentenceReconstruct"] = ""

  for sentence in sentences:
    response["sentenceReconstruct"] += sentence + "."
    sentenceBlob = TextBlob(sentence)

    sentenceAnalysis = {}
    sentenceAnalysis["words"] = []
    
    for word in sentence.split(" "):
      wordBlob = TextBlob(word)
      wordAnalysis = {}
      wordAnalysis["source"] = word
      wordAnalysis["polarity"] = wordBlob.sentiment.polarity
      wordAnalysis["subjectivity"] = wordBlob.sentiment.subjectivity
      sentenceAnalysis["words"].append(wordAnalysis)
    
    sentenceAnalysis["source"] = sentence
    sentenceAnalysis["polarity"] = sentenceBlob.sentiment.polarity
    sentenceAnalysis["subjectivity"] = sentenceBlob.sentiment.subjectivity
    
    response["sentences"].append(sentenceAnalysis)
    response["sentencecount"] += 1

  return response


@app.route('/api/analysis/text', methods=['GET', 'POST'])
def api_analyze_text():
  requestItem = request.json

  # Analyze text from request
  text = requestItem["text"]
  response = get_text_analysis(text)

  return jsonify(response)

# def extract_text_from_url(pageUrl):

#   try:
#     page = urllib2.urlopen(quote_page)
#   except urllib2.HTTPError, err:
#     return False

#   soup = BeautifulSoup(page, 'html.parser')

#   return soup.get_text()

# @app.route('/api/analysis/url', methods=['GET'])
# def api_analyze_url():
#   reqeustItem = request.json

#   # Analyze text from URL
#   pageUrl = requestItem["url"]
#   text = extract_text_from_url(pageUrl)
#   response = get_text_analysis(text)

#   if(not response):
#     raise CannotProcessURL('Could not load the page!', status_code=404)

#   return jsonify(response)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80)