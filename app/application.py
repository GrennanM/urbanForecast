from flask import Flask, render_template
from firebase import firebase
from datetime import datetime, timedelta
from settings import *

# get readings from Firebase
firebase = firebase.FirebaseApplication(myUrl, None)
weatherResults = firebase.get('/weather', None)

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
    return render_template("home.html",  waterTemp=getCurrentWaterTemperature(),
                           airTemp=getCurrentAirTemperature())
