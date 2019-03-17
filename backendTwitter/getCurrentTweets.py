""""Parses text from DublinBayBuoy twitter (https://twitter.com/DublinBayBuoy),
adds data to local db and posts to Firebase as json"""

import tweepy
import re
import dataset
from datetime import datetime
from settings import *
from main import *
from firebase import firebase


# Authenticate with Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Create api to connect to twitter with credentials
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True, compression=True)

# local db
db = dataset.connect('sqlite:///dublinBayBuoydb2.db')
table = db['dublinBBTable2']

# Firebase authentication
firebase = firebase.FirebaseApplication(myUrl, None)

# Create a listener
class StreamListener(tweepy.StreamListener):

    def on_error(self, status_code):

        print ("Error... status code: ", status_code)
        if status_code == 420: # rate limit is reached
            return False
        return True


    def on_status(self, status):

        # post parsed tweet to firebase
        tweet = status.text
        try:
            parsedTweet = parseTweet(tweet)
            firebase.post('/weather', parsedTweet)
        except:
            print ("Failed to parse tweet")

        # add tweet to local db
        try:
            table.insert(parsedTweet)
        except Exception as e:
            print("Failed to post to db: ", e)


# listen for new tweets from DublinBayBuoy
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(follow=DUBLINBAYBUOY_ID)
