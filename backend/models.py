from abc import ABC, abstractmethod

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
s = SentimentIntensityAnalyzer()

<<<<<<< HEAD
import flair
flair_sentiment = flair.models.TextClassifier.load('en-sentiment')

""" from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
azureclient = TextAnalyticsClient(endpoint="https://textsentimentcheck.cognitiveservices.azure.com/", credential=AzureKeyCredential("36e55f902483497bae2aa7bcbb663a52")) """
=======
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
azureclient = TextAnalyticsClient(endpoint="https://textsentimentcheck.cognitiveservices.azure.com/", credential=AzureKeyCredential("36e55f902483497bae2aa7bcbb663a52"))
>>>>>>> 62fa02f69ce808ca6286af29c35cf976c5722860

# add an instance of your model to this once you have defined it
models = []

# all added sentiment analysis models must be wrapped
# in a class that inherits from this class to enforce
# a common api between different models
class baseSentimentModel(ABC):
    def __init__(self, name, model):
        self.name = name
        self.model = model

    # this is the only required method
    # it should take the text and return the predicted
    # sentiment as a number between [-1, 1] where
    # 1 is maximally positive, 0 is nuetral, and -1 is maximally negative
    @abstractmethod
    def predict(self, texts):
        pass

class nltkModel(baseSentimentModel):
    def predict(self, texts):
        return [self.parsePolarity(self.model.polarity_scores(text)) for text in texts]
    def parsePolarity(self, polarity):
        if polarity['neg'] > polarity['pos'] and polarity['neg'] > polarity['neu']:
            return -1.0
        elif polarity['pos'] > polarity['neg'] and polarity['pos'] > polarity['neu']:
            return 1.0
        return 0.0

models.append(nltkModel('nltkVader', s))

class flairModel(baseSentimentModel):
    def __init__(self, name, model):
        self.sentMapping = {'NEGATIVE' : -1.0, 'NEUTRAL': 0.0, 'POSITIVE': 1.0}
        super().__init__(name, model)
    def predict(self, texts):
        sents = [flair.data.Sentence(text) for text in texts]
        self.model.predict(sents)
        return [self.sentMapping[t.labels[0].value] for t in sents]

models.append(flairModel('flair', flair_sentiment))

""" class azureModel(baseSentimentModel):
    def predict(self, texts):
        responses = self.model.analyze_sentiment(documents=texts)

        return list(map(self.parseResponses, responses))
        
    def parseResponses(self, responses):
        totals = [0.0, 0.0, 0.0]
        for response in responses:
            totals[0] += response.confidence_scores.positive
            totals[1] += response.confidence_scores.neutral
            totals[2] += response.confidence_scores.negative

        max_idx = 0
        if totals[1] > totals[0]:
            max_idx = 1
        if totals[2] > totals[max_idx]:
            max_idx = 2
        
        return 1.0 - max_idx # this returns 1.0 for pos, 0.0 for neutral, and -1.0 for negative

models.append(azureModel('azureModel', azureclient)) """




"""
example of this:

class azureModel(baseSentimentModel):
    def predict(self, text):
        response = self.model.analyze_sentiment(documents=text)[0]
        return response.confidence_scores.positive + response.confidence_scores.negative

models.append(azureModel('azureModel', azureclient))



