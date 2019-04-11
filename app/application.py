from flask import Flask, render_template
from firebase import firebase
from datetime import datetime, timedelta
from settings import *

# get readings from Firebase
firebase = firebase.FirebaseApplication(myUrl, None)
weatherResults = firebase.get('/weather', None)

def getCurrentWeather(numberReadings):
    """input: number of weather readings (int),
    returns: most recent weather readings from firebase (list)"""

    weatherList = []
    currentWeather = []
    for weatherReading in weatherResults.values():
        currentWeather.extend([weatherReading['roundedTime'], weatherReading['waveHeight'],
                               weatherReading['compassDir'], weatherReading['avgWind'],
                               weatherReading['tideHeight'], weatherReading['starRating']])
        weatherList.append(currentWeather)
        currentWeather = []

    return weatherList[-numberReadings-1:-1:1]


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
    for i in range(1, 3):
        result += airTempList[-i]

    averageAirTemp = round(result / 2, 1)

    return averageAirTemp


app = Flask(__name__)

@app.route('/')
def homePage():
    return render_template("home.html", weatherList=getCurrentWeather(9), waterTemp=getCurrentWaterTemperature(),
                           airTemp=getCurrentAirTemperature())


@app.route('/waveHeight')
def displayWaveHeight():
    return render_template("waveHeight.html", waterTemp=getCurrentWaterTemperature(),
                           airTemp=getCurrentAirTemperature())


@app.route('/tide')
def displayTide():
    return render_template("tide.html", waterTemp=getCurrentWaterTemperature(),
                           airTemp=getCurrentAirTemperature())
