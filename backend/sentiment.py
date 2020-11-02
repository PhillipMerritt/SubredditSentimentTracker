from models import models
from tqdm import tqdm
from collections import defaultdict

def getSentiment(comments, links):
    # [['Time Frame', 'Sentiment', { "role": 'style' }]]

    # create a dict of data lists for each model
    # as well as a dict to track the average thread sentiment
    output = {}
    threads = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    for model in models:
        output[model.name] = {"sentiment": 0.0, "most_positive": "", "most_negative": ""}

    # sum the sentiment of each comment for each model inidividually
    
    for model in models:
        sentiments = model.predict(comments)

        for i, sentiment in enumerate(sentiments):
            output[model.name]["sentiment"] += sentiment
            threads[model.name][links[i]][0] += sentiment
            threads[model.name][links[i]][1] += 1
    
    # if this isn't an empty bin divide each sum to get the average
    if comments:
        for model in models:
            output[model.name]["sentiment"] /= len(comments)

            """ for thread in threads[model.name].keys():
                threads[model.name][thread] = threads[model.name][thread][0] / threads[model.name][thread][1] """
            
            most_neg, most_pos = "", ""
            low, high = 99999.0, -99999.0
            for thread in threads[model.name].keys():
                val = threads[model.name][thread][0]
                if val < low:
                    low = val
                    most_neg = thread
                if val > high:
                    high = val
                    most_pos = thread

            output[model.name]["most_positive"] = most_pos
            output[model.name]["most_negative"] = most_neg



    return output
        
