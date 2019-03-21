from flask import Flask, render_template
from firebase import firebase
from datetime import datetime, timedelta
from settings import *

# get readings from Firebase
firebase = firebase.FirebaseApplication(myUrl, None)
weatherResults = firebase.get('/weather', None)

def getCurrentWeather():
    """returns: last 4 weather readings from firebase"""
    weatherList = []
    currentWeather = []
    for weatherReading in weatherResults.values():
        currentWeather.extend([weatherReading['roundedTime'], weatherReading['waveHeight'],
                               weatherReading['compassDir'], weatherReading['avgWind'],
                               weatherReading['tideHeight'], weatherReading['starRating']])
        weatherList.append(currentWeather)
        currentWeather = []

    return weatherList[-5:-1:1]


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
def homePage():
    return render_template("home.html", weatherList=getCurrentWeather(), waterTemp=getCurrentWaterTemperature(),
                           airTemp=getCurrentAirTemperature())
