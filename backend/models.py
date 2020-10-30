from abc import ABC, abstractmethod
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
s = SentimentIntensityAnalyzer()

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
azureclient = TextAnalyticsClient(endpoint="https://textsentimentcheck.cognitiveservices.azure.com/", credential=AzureKeyCredential("36e55f902483497bae2aa7bcbb663a52"))

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
    def predict(self, text):
        pass

class nltkModel(baseSentimentModel):
    def predict(self, text):
        return self.model.polarity_scores(text)['compound']

models.append(nltkModel('nltkVader', s))


class azureModel(baseSentimentModel):
    def predict(self, text):
        response = self.model.analyze_sentiment(documents=text)[0]
        return response.confidence_scores.positive + response.confidence_scores.negative

models.append(azureModel('azureModel', azureclient))



