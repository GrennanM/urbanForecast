from firebase import firebase
from datetime import datetime
from settings import *
import matplotlib.pyplot as plt


# get readings from Firebase
firebase = firebase.FirebaseApplication(myUrl, None)
weatherResults = firebase.get('/weather', None)

# get current times, wave heights, wind speeds
dateTimeObj = [datetime.strptime(t['dateTime'], '%Y-%m-%dT%H:%M:%S')
               for t in weatherResults.values()]
times = [t.time() for t in dateTimeObj]
waveHeights = [w['waveHeight'] for w in weatherResults.values()]
windSpeed = [ws['avgWind'] for ws in weatherResults.values()]
tides = [t['tideHeight'] for t in weatherResults.values()]


def plotWaveHeightWindSpeed():
    """plot wave height and wind speed vs time"""

    fig, ax1 = plt.subplots()
    plt.grid(True)

    color = 'tab:red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Wave Height (m)', color=color)
    plt.ylim(0,)
    ax1.plot(times, waveHeights, color=color)
    plt.gcf().autofmt_xdate()
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel('Wind Speed (knots)', color=color)
    ax2.plot(times, windSpeed, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    return plt.savefig(staticFilePath + "waveHeight_windSpeed.png")


def plotTides():
    """plot current tide height"""

    fig, ax1 = plt.subplots()
    plt.grid(True)

    plt.plot(times, tides)
    plt.gcf().autofmt_xdate()
    plt.xlabel("Time")
    plt.ylabel("Tide Height (m)")

    return plt.savefig(staticFilePath + "currentTide.png")
