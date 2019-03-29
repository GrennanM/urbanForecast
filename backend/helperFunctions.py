import re
from datetime import datetime, timedelta
from settings import *
import math
from urllib.request import urlopen
from bs4 import BeautifulSoup
from firebase import firebase

METRE_CONVERSION = 0.3048 # to convert from feet to metres


def getTideTimesAndTideHeights():
    """scrapes www.tide-forecast.com to collect current tide information.
    returns: 2 lists, first list contains first two tide times for current date,
    second list contain first two tide heights for current dates"""

    html = urlopen(urlTidesInfo)
    soup = BeautifulSoup(html, 'lxml')

    # scrape url to gather current tide time and height
    tideTimes = soup.find_all("td", "time tide", limit=2)
    tideHeightImperial = soup.find_all("span", "imperial", limit=2)

    # remove html tags
    tideTimes = [t.get_text() for t in tideTimes]
    tideHeightImperial = [h.get_text() for h in tideHeightImperial]

    # parse string and remove tide height, convert from imperial to metres
    tideHeightsFinal = []
    for h in tideHeightImperial:
        height = float(''.join([i for i in h if i.isdigit() or i == "."]))
        height *= METRE_CONVERSION
        tideHeightsFinal.append(round(height, 1))

    # parse string and remove time, convert to float
    tideTimesFinal = []
    for t in tideTimes:
        time = ''.join([i for i in t if i.isdigit() or i == ":"])
        time = convertTimeToFloat(time)
        tideTimesFinal.append(time)

    return tideTimesFinal, tideHeightsFinal


def getCurrentTideHeight(currentTimeString):
    """estimates current tide height given local time,
    input: current time as rounded string (hours:minutes),
    output: estimate of tide height"""

    # convert time in hours:minutes as string to float
    currentTimeFloat = convertTimeToFloat(currentTimeString)

    # get current tide time and tide height information
    tideTimes, tideHeight = getTideTimesAndTideHeights()

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


def getStarRating(waveHeight, windDir, avgWind, tideHeight):
    """returns a star rating between 0 and 5 for current conditions,
    input: waveHeight, windDir, avgWind, tideHeight,
    output: starRating (int)"""

    starRating = 0

    # wave height
    if waveHeight > 2:
        starRating += 4
    elif waveHeight > 1.6:
        starRating += 3
    elif waveHeight > 1.4:
        starRating += 2
    elif waveHeight > 1.2:
        starRating += 1

    # wind direction
    if windDir >= 270 or windDir <= 30:
        starRating += 1

    # wind strength
    if avgWind < 15:
        starRating += 1

    # tide
    if tideHeight < 1.2:
        starRating += 1
    elif tideHeight > 2.2:
        starRating = 1

    # check upper bound of 5 stars
    if starRating > 5:
        starRating = 5
    elif waveHeight < 1:
        starRating = 0

    return starRating


def roundTime(dateTimeString):
    """rounds a datetime string to nearest 20 minutes,
    input: dateTimeString, output: time as string (hours:minutes)"""

    dateTimeObj = datetime.strptime(dateTimeString, '%d/%m/%Y %H:%M:%S')

    # round to nearest 20 minute
    discard = timedelta(minutes=dateTimeObj.minute % 20)
    dateTimeObj -= discard
    if discard > timedelta(minutes=10):
        dateTimeObj += timedelta(minutes=20)

    result = dateTimeObj.strftime('%H:%M')

    return result


def convertTimeToFloat(timeString):
    """input: time in hours:minutes
    output: time as float"""

    currentTimeList = timeString.split(":")
    currentTimeFloat = round(
        float(currentTimeList[0]) + float(currentTimeList[1]) / 60, 2)

    return currentTimeFloat


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

    # add star rating
    waveHeight=float(waveHeight.group().split(":")[1])
    windDir=float(windDirection.group().split(":")[1])
    avgWind=float(avgWind.group().split(":")[1])
    starRating = getStarRating(waveHeight, windDir, avgWind, tideHeight)

    try:
        parsedTweet = dict(waterTemp=float(waterTemp.group().split(":")[1]),
                     waveHeight=waveHeight,
                     windDir=windDir,
                     gustDir=float(gustDirection.group().split(":")[1]),
                     avgWind=avgWind,
                     gust=float(gust.group().split(":")[1]),
                     dateTime=dateTimeObject,
                     roundedTime=roundedTime,
                     compassDir=compassDir,
                     tideHeight=tideHeight,
                     starRating=starRating)
    except Exception as e:
        print ("Failed to parse tweet")
        return None

    return parsedTweet
