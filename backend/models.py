from abc import ABC, abstractmethod

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
s = SentimentIntensityAnalyzer()

import flair
flair_sentiment = flair.models.TextClassifier.load('en-sentiment')

""" from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
azureclient = TextAnalyticsClient(endpoint="https://textsentimentcheck.cognitiveservices.azure.com/", credential=AzureKeyCredential("36e55f902483497bae2aa7bcbb663a52")) """

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
        result = []
        for i, t in enumerate(sents):

            try:
                result.append(self.sentMapping[t.labels[0].value])
            except:
                print(texts[i])
        return result

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

class myModel(baseSentimentModel):
    # this example is a categorical model
    # so the values must be converted to numbers
    def predict(self, text):
        pred = self.model.evaluateSentiment(text)

        if pred == 'positive':
            return 1.0
        elif pred == 'nuetral':
            return 0.0
        else:
            return -1.0

models.append(myModel('example model', somePackage.model))
"""