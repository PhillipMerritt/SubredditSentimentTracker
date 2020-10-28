from models import models
from tqdm import tqdm

def getSentiment(comments):
    # [['Time Frame', 'Sentiment', { "role": 'style' }]]

    # create a dict of data lists for each model
    output = {}
    for model in models:
        output[model.name] = 0.0

    # sum the sentiment of each comment for each model inidividually
    for comment in comments:
        for model in models:
            sentiment = model.predict(comment)
            output[model.name] += sentiment
    
    # if this isn't an empty bin divide each sum to get the average
    if comments:
        for model in models:
            output[model.name] /= len(comments)

    return output
        
