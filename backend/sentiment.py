import json
import urllib.request, json 
from models import models

from datetime import datetime
import time

from tqdm import tqdm
import re

def convertDateString(date):
    year, month, day = date.split('-')
    return datetime(int(year), int(month), int(day))

def convertToPosix(date):
    return int(time.mktime(date.timetuple()))

def getBinIndex(before, current):
    delta = current - before
    return (delta.days * 4) + int(delta.seconds / 21600)

def getComments(sub, after_str, before_str):
    # converts dates like '2020-10-05' to datetime objects
    before, after = convertDateString(before_str), convertDateString(after_str)
    # convert these to unix timestamps to use in the api 
    # unix timestamps are the number of seconds since January 1st 1970
    start, end = convertToPosix(after), convertToPosix(before)

    bins = []

    # for each 6 hour period between start and end
    for start in tqdm(list(range(start, end, 21600))):
        # add a new bin
        bins.append([])
        # create a url to request all of the comments between the current value of start and start + 6 hours
        url = 'https://api.pushshift.io/reddit/search/comment/?title='+'&size=10000&after='+str(start)+'&before='+str(start + 86400)+'&subreddit='+str(sub)
        # get the data
        with urllib.request.urlopen(url) as url:
            # parse it into a python object
            post_data = json.loads(url.read().decode())

            # for each comment
            for i in post_data['data']:
                #get comment
                comment = i['body']

                # skip empty, removed, or deleted comments
                if re.match(r'^(\s*\[(removed|deleted)\]\s*)|(\s*)$', comment):
                    continue
                
                # add comment to bin
                bins[-1].append(comment)

    return bins

def getSentiments(sub, before, after):
    # get comments for the time frame
    comments = getComments(sub, before, after)
    # create a dict of data lists for each model
    output = {}
    for model in models:
        output[model.name] = []

    # for each bin of comments
    for bin in comments:
        # add another value to each data list
        for model in models:
            output[model.name].append(0.0)

        # sum the sentiment of each comment for each model inidividually
        for comment in bin:
            for model in models:
                sentiment = model.predict(comment)
                output[model.name][-1] += sentiment
        
        # if this isn't an empty bin divide each sum to get the average
        if bin:
            for model in models:
                output[model.name][-1] /= len(bin)

    return output
        
