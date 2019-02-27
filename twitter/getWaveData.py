""""parses text from DublinBayBuoy twitter (https://twitter.com/DublinBayBuoy),
adds data to local db and posts to Firebase as json"""

import json
import tweepy
import requests
import re
import dataset
from datetime import datetime
import ast
from settings import *


# Authenticate with Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Create api to connect to twitter with credentials
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True, compression=True)

db = dataset.connect('sqlite:///dublinBayBuoydb2.db')


def parseTweet(tweet):
    """parses tweet from DublinBayBuoy, input: tweet (string),
    output: dictionary of parsed tweet"""

    # Parse data using re
    waterTemp = re.search(r'Water Temp:[0-9].[0-9]|Water Temp:[0-9]', tweet)
    waveHeight = re.search(r'Wave Height:[0-9].[0-9]|Wave Height:[0-9]', tweet)
    windDirection = re.search(r'Wind Dir:[0-9][0-9][0-9]|Wind Dir:[0-9]|Wind Dir:[0-9]', tweet)
    gustDirection = re.search(r'Gust Dir:[0-9][0-9][0-9]|Gust Dir:[0-9]|Gust Dir:[0-9]', tweet)
    avgWind = re.search(r'Avg Wind:[0-9][0-9]|Avg Wind:[0-9]', tweet)
    gust = re.search(r'Gust:[0-9][0-9]|Gust:[0-9]', tweet)
    dateTimeTemp = re.search(r'at .*', tweet)

    # convert dateTime to datetimeObject
    dateTime = dateTimeTemp.group().split(" ")[1] + " " + dateTimeTemp.group().split(" ")[2]
    dateTimeObject = datetime.strptime(dateTime, '%d/%m/%Y %H:%M:%S')

    parsedTweet = dict(waterTemp=float(waterTemp.group().split(":")[1]),
                 waveHeight=float(waveHeight.group().split(":")[1]),
                 windDir=float(windDirection.group().split(":")[1]),
                 gustDir=float(gustDirection.group().split(":")[1]),
                 avgWind=float(avgWind.group().split(":")[1]),
                 gust=float(gust.group().split(":")[1]),
                 dateTime=dateTimeObject)

    return parsedTweet


def addTweetToDb(parsedTweet):
    """adds parsed tweet to db, input: dictionary, output: none"""

    table = db['dublinBBTable2']

    try:
        table.insert(parsedTweet)
    except Exception as e:
        print("Failed to post to db: ", e)


def postToFirebase(parsedTweet):
    """post parsed tweet to Firebase, input: dict, output: none"""

    # convert datetime object to string for posting to Firebase
    tweetDump = json.dumps(parsedTweet, default=str)
    tweetDict = ast.literal_eval(tweetDump)

    try:
        requests.post(url=myUrl, json=tweetDict)
    except Exception as e:
        print ("Failed to post to Firebase: ", e)


# Create a listener
class StreamListener(tweepy.StreamListener):

    def on_error(self, status_code):

        print ("Error... status code: ", status_code)
        if status_code == 420: # rate limit is reached
            return False
        return True

    def on_status(self, status):

        tweet = status.text # record text of tweet
        parsedTweet = parseTweet(tweet)
        addTweetToDb(parsedTweet)
        postToFirebase(parsedTweet)


# listen for new tweets from DublinBayBuoy
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(follow=dublinBayBuoy)
