#!/usr/bin/env python

"""Reads temperature from serial port and posts to Firebase"""

import serial
import re
from datetime import datetime
import json
import requests
import dataset


myUrl = 'XXXXXXXXXXX'

ser = serial.Serial('/dev/ttyACM0', 9600)

# read temperature from serial port and convert to float
temp = str(ser.readline())
tempFloat = float(re.search(r'[0-9][0-9].[0-9][0-9]', temp)[0])

# add timestamp
currentTime = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# post to Firebase
json = {'Temperature': tempFloat, 'dateTime': currentTime}
requests.post(url=myUrl, json=json)

# add to local db
db = dataset.connect('sqlite:///temperature.db')
table = db['tempTable']
table.insert(json)
