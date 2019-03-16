import json
import requests
import re
import dataset
from datetime import datetime, timedelta
import ast
from settings import *


def roundTime(dateTimeString):
    """rounds a datetime string to nearest 20 minutes,
    input: dateTimeString, output: timeString"""

    dateTimeObj = datetime.strptime(dateTimeString, '%d/%m/%Y %H:%M:%S')

    # round to nearest 20 minute
    discard = timedelta(minutes=dateTimeObj.minute % 20)
    dateTimeObj -= discard
    if discard >= timedelta(minutes=10):
        dateTimeObj += timedelta(minutes=20)

    result = dateTimeObj.strftime('%H:%M')

    return result

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

    # round time
    roundedTime = roundTime(dateTime)

    try:
        parsedTweet = dict(waterTemp=float(waterTemp.group().split(":")[1]),
                     waveHeight=float(waveHeight.group().split(":")[1]),
                     windDir=float(windDirection.group().split(":")[1]),
                     gustDir=float(gustDirection.group().split(":")[1]),
                     avgWind=float(avgWind.group().split(":")[1]),
                     gust=float(gust.group().split(":")[1]),
                     dateTime=dateTimeObject,
                     roundedTime=roundedTime)
    except Exception as e:
        print ("Failed to parse tweet")
        return None

    return parsedTweet


def postToFirebase(parsedTweet):
    """post parsed tweet to Firebase, input: dict, output: none"""

    # convert datetime object to string for posting to Firebase
    tweetDump = json.dumps(parsedTweet, default=str)
    tweetDict = ast.literal_eval(tweetDump)

    try:
        requests.post(url=myUrl, json=tweetDict)
    except Exception as e:
        print ("Failed to post to Firebase: ", e)