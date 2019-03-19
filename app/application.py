from flask import Flask, render_template
from firebase import firebase
from datetime import datetime, timedelta
from settings import *

# get readings from Firebase
firebase = firebase.FirebaseApplication(myUrl, None)
weatherResults = firebase.get('/weather', None)

def getCurrentWeather():
    """returns: last 10 weather readings from firebase"""
    weatherList = []
    currentWeather = []
    for weatherReading in weatherResults.values():
        currentWeather.extend([weatherReading['roundedTime'], weatherReading['waveHeight'],
                               weatherReading['compassDir'], weatherReading['avgWind'],
                               weatherReading['tideHeight'], weatherReading['starRating']])
        weatherList.append(currentWeather)
        currentWeather = []

    return weatherList[-1:]
    # return weatherList


def getCurrentWaterTemperature():
    """returns average of last 10 water temperature readings from db"""

    # get water temperature readings
    waterTempList = [w['waterTemp'] for w in weatherResults.values()]

    result = 0
    for i in range(2):
        result += waterTempList[-i]

    averageWaterTemp = round(result / 2, 1)

    return averageWaterTemp

def getCurrentAirTemperature():
    """returns average of last two air temperature readings from db"""

    # get air temperatures from firebase
    airTemps = firebase.get('/airTemp', None)
    airTempList = [a['temp'] for a in airTemps.values()]

    result = 0
    for i in range(2):
        result += airTempList[-i]

    averageAirTemp = round(result / 2, 1)

    return averageAirTemp


app = Flask(__name__)

@app.route('/')
def helloWorld():
    return render_template("home.html", weatherList=getCurrentWeather(),
                           waterTemp=getCurrentWaterTemperature(),
                           airTemp=getCurrentAirTemperature())


# export FLASK_APP=application.py
# export FLASK_ENV=development

# to do:
# parse and round time to nearest 20
# display last 20 readings
# display wind direction
# display tide
# display water and air temp in nav bar
# display star rating
# graph wave height
# insert image
# update table in real time (js)
