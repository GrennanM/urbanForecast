import json
import requests
import re
import dataset
from datetime import datetime, timedelta
import ast
from settings import *
import math

# hard coded tide times and tide heights for 16th March
tideTimes = [0, 7, 13, 19.6]
tideHeight = [1.4, 3.3, 1.2, 3.4]

def convertTimeToFloat(timeString):
    """input: time in hours:minutes
    output: time as float"""

    currentTimeList = timeString.split(":")
    currentTimeFloat = round(
        float(currentTimeList[0]) + float(currentTimeList[1]) / 60, 2)

    return currentTimeFloat


def getCurrentTideHeight(currentTimeString):
    """input: current time as rounded string (hours:minutes),
    output: height of tide"""

    currentTimeFloat = convertTimeToFloat(currentTimeString)

    # get high and low tide, and time of first High tide
    if tideHeight[0] > tideHeight[1]:
        highTideHeight = tideHeight[0]
        lowTideHeight = tideHeight[1]
        firstHighTideTime = tideTimes[0]
    else:
        highTideHeight = tideHeight[1]
        lowTideHeight = tideHeight[0]
        firstHighTideTime = tideTimes[1]

    amplitude = (highTideHeight - lowTideHeight) / 2
    midway = amplitude + lowTideHeight
    timeFromFirstHighTide = currentTimeFloat - firstHighTideTime

    currentTideHeight = round(midway + abs(amplitude) * math.cos(0.5 * timeFromFirstHighTide), 1)

    return currentTideHeight


def getCompassDirections(windDir):
    """input: str between 0 and 360,
    output: compass bearing"""

    compassDict = {1:'N', 2:'NNE', 3:'NE', 4:'ENE', 5:'E', 6:'ESE', 7:'SE',
                    8:'SSE', 9:'S', 10:'SSW', 11:'SW', 12:'WSW', 13:'W',
                    14:'WNW', 15:'NW', 16:'NNW', 17:'N'}

    windDirDegrees = float(windDir)
    compassIndex = round(windDirDegrees/22.5) + 1

    return compassDict[compassIndex]


def roundTime(dateTimeString):
    """rounds a datetime string to nearest 20 minutes,
    input: dateTimeString, output: time as string (hours:minutes)"""

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

    # convert dateTime to datetimeObject for local db
    dateTime = dateTimeTemp.group().split(" ")[1] + " " + dateTimeTemp.group().split(" ")[2]
    dateTimeObject = datetime.strptime(dateTime, '%d/%m/%Y %H:%M:%S')

    # add time rounded to nearest 20 minutes
    roundedTime = roundTime(dateTime)

    # add compass direction
    windDirect = float(windDirection.group().split(":")[1])
    compassDir = getCompassDirections(windDirect)

    # add tide height
    tideHeight = getCurrentTideHeight(roundedTime)

    try:
        parsedTweet = dict(waterTemp=float(waterTemp.group().split(":")[1]),
                     waveHeight=float(waveHeight.group().split(":")[1]),
                     windDir=float(windDirection.group().split(":")[1]),
                     gustDir=float(gustDirection.group().split(":")[1]),
                     avgWind=float(avgWind.group().split(":")[1]),
                     gust=float(gust.group().split(":")[1]),
                     dateTime=dateTimeObject,
                     roundedTime=roundedTime,
                     compassDir=compassDir,
                     tideHeight=tideHeight)
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
