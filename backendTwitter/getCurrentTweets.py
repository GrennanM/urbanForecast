""""Parses text from DublinBayBuoy twitter (https://twitter.com/DublinBayBuoy),
adds data to local db and posts to Firebase as json"""

import json
import tweepy
import requests
import re
import dataset
from datetime import datetime
import ast
from settings import *
from helperFunctions import *


# Authenticate with Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Create api to connect to twitter with credentials
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True, compression=True)

db = dataset.connect('sqlite:///dublinBayBuoydb2.db')
table = db['dublinBBTable2']


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

        # add tweet to local db
        try:
            table.insert(parsedTweet)
        except Exception as e:
            print("Failed to post to db: ", e)

        postToFirebase(parsedTweet)


# listen for new tweets from DublinBayBuoy
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(follow=DUBLINBAYBUOY_ID)
