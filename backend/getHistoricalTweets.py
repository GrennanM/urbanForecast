"""Parses text from DublinBayBuoy twitter (https://twitter.com/DublinBayBuoy),
adds historical tweets from timeline to local db"""

import tweepy
from settings import *
from commonFunctions import *

DUBLINBAYBUOY_ID = 2320627075

# Authenticate with Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Create api to connect to twitter with credentials
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True, compression=True)


db = dataset.connect('sqlite:///dublinBBHistorical2.db')
table = db['historical']


# get historical tweets from timeline
for status in tweepy.Cursor(api.user_timeline, id=DUBLINBAYBUOY_ID).items():

    tweet = status.text
    parsedTweet = parseTweet(tweet)

    # add tweet to local db
    try:
        table.insert(parsedTweet)
    except Exception as e:
        print("Failed to post to db: ", e)


# # print number of rows in db
# print(len(table))
