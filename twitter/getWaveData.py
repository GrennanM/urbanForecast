import json
import tweepy
import requests
import re
import dataset
from settings import *
from datetime import datetime

# Authenticate with Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Create api to connect to twitter with creadentials
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True, compression=True)

db = dataset.connect('sqlite:///dublinBayBuoydb.db')

# Create a listener
class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        # record text of tweet
        tweet = status.text

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

        # add tweet to db
        table = db['dublinBBTable']
        try:
            table.insert(dict(waterTemp=float(waterTemp.group().split(":")[1]),
                         waveHeight=float(waveHeight.group().split(":")[1]),
                         windDir=float(windDirection.group().split(":")[1]),
                         gustDir=float(gustDirection.group().split(":")[1]),
                         avgWind=float(avgWind.group().split(":")[1]),
                         gust=float(gust.group().split(":")[1]),
                         dateTime=dateTimeObject))
        except ProgrammingError as err:
            print(err)

    def on_error(self, status_code):
        print ("Error... status code: ", status_code)
        if status_code == 420: # rate limit is reached
            return False
        return True

# listen for new tweets from DublinBayBuoy
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(follow=dublinBayBuoy)
