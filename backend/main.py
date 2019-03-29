""""Parses text from DublinBayBuoy twitter (https://twitter.com/DublinBayBuoy),
adds data to local db and posts to Firebase as json"""

import tweepy
import re
from datetime import datetime
from settings import *
from helperFunctions import *
from graphs import *
from firebase.firebase import FirebaseApplication


# Authenticate with Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Create api to connect to twitter with credentials
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True, compression=True)

# Firebase authentication
app = FirebaseApplication(myUrl, None)

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
            app.post('/weather', parsedTweet)
        except:
            print ("Failed to parse tweet")

        # update graphs
        plotTides()
        plotWaveHeightWindSpeed()


# listen for new tweets from DublinBayBuoy
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(follow=DUBLINBAYBUOY_ID)
