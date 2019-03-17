from flask import Flask, render_template
from firebase import firebase
from datetime import datetime, timedelta
from settings import *

# get readings from Firebase
firebase = firebase.FirebaseApplication(myUrl, None)
results = firebase.get('', None)


def getCurrentWeather():
    """returns: last 10 weather readings from firebase"""
    weatherList = []
    currentWeather = []
    for weatherReading in results.values():
        currentWeather.extend([weatherReading['roundedTime'], weatherReading['waveHeight'],
                               weatherReading['compassDir'], weatherReading['avgWind'],
                               weatherReading['tideHeight']])
        weatherList.append(currentWeather)
        currentWeather = []

    # return weatherList[-10:]
    return weatherList


def getCurrentWaterTemperature():
    """returns average of last 10 water temperature readings from db"""

    # get water temperature readings
    waterTempList = [w['waterTemp'] for w in results.values()]

    result = 0
    for i in range(10):
        result += waterTempList[-i]

    averageWaterTemp = round(result / 10, 1)

    return averageWaterTemp


app = Flask(__name__)


@app.route('/')
def helloWorld():
    return render_template("home.html", weatherList=getCurrentWeather(),
                           waterTemp=getCurrentWaterTemperature())


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
