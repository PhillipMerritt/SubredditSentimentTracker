import json
import urllib.request, json 

from datetime import datetime
#from datetime import time
import time

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
s = SentimentIntensityAnalyzer()
from tqdm import tqdm
import re

a = "00:00:00"
a = datetime.strptime(a, '%H:%M:%S')
b = "06:00:00"
b = datetime.strptime(b, '%H:%M:%S')
c = "12:00:00"
c = datetime.strptime(c, '%H:%M:%S')
d = "18:00:00"
d = datetime.strptime(d, '%H:%M:%S')

def convertDateString(date):
    year, month, day = date.split('-')
    return datetime(int(year), int(month), int(day))

def convertToPosix(date):
    return int(time.mktime(date.timetuple()))

def getBinIndex(before, current):
    delta = current - before
    return (delta.days * 4) + int(delta.seconds / 21600)

def getComments(sub, before_str, after_str):
    before, after = convertDateString(before_str), convertDateString(after_str)
    start, end = convertToPosix(before), convertToPosix(after)

    bins = []

    for start in tqdm(list(range(start, end, 21600))):
        bins.append([])
        url = 'https://api.pushshift.io/reddit/search/comment/?title='+'&size=10000&after='+str(start)+'&before='+str(start + 86400)+'&subreddit='+str(sub)
        with urllib.request.urlopen(url) as url:
            post_data = json.loads(url.read().decode())

            for i in post_data['data']:
                #get comment
                comment = i['body']

                if re.match(r'^(\s*\[(removed|deleted)\]\s*)|(\s*)$', comment):
                    continue
                #get time
                t = i['created_utc'] 
                #get bin index
                #bin_idx = getBinIndex(before, datetime.utcfromtimestamp(t))

                bins[-1].append(comment)

    return bins

def getSentiments(sub, before, after):
    comments = getComments(sub, before, after)
    output = []

    for bin in comments:
        total = 0.0

        for comment in bin:
            sentiment = s.polarity_scores(comment)['compound']
            total += sentiment
        
        if len(bin) == 0:
            output.append(0.0)
        else:
            output.append(total / len(bin))

    return output
        
