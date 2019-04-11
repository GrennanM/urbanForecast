# !/usr/bin/env python

"""Reads temperature from serial port every 5 minutes and posts to Firebase"""

import serial
import re
from datetime import datetime, timedelta
from settings import *
import time
from firebase.firebase import FirebaseApplication

# Firebase authentication
app = FirebaseApplication(myUrl, None)


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


# define serial port
ser = serial.Serial('/dev/ttyACM0', 9600)

while True:
    # read temperature from serial port and convert to float
    temp = str(ser.readline())
    tempFloat = round(float(re.search(r'[0-9][0-9].[0-9][0-9]', temp)[0]), 1)

    # add timestamp
    currentTime = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    roundedTime = roundTime(currentTime)

    # post temp to Firebase
    toPost = {"temp": tempFloat, 'dateTime': currentTime,
              'roundedTime': roundedTime}
    app.post('/airTemp', toPost)

    time.sleep(20)
