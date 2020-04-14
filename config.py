#!/usr/bin/env python3
#encoding: utf-8

# @Morodin 14/04/202
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import DHT

SETTINGS = {
    "DHT_GPIO":                 27,                 # GPIO Number (BCM) of the DHT Sensor
    "DHT_SENSOR":               DHT.DHTAUTO,        # DHT.DHT11, DHT.DHTXX or DHT.DHTAUTO
    "FAN_GPIO":                 5,                  # GPIO Number (BCM) for the Relay
    "FAN_THRESHOLD":            35,                 # in Celsius. Above this value, the fan will be turned on
    "THRESHOLD_HOUR":           14,                 # hour to use PM WINDOW_THRESHOLD
    "WINDOW_THRESHOLD":         [22, 25],           # in Celsius. Above this value, windows will be opened by the servo, [AM, PM]
    "TRIX_THRESHOLD":           18,                 # trix open if above this temperature
    "TRIX_MONTH":               9,                  # from this month we trick the plants into fruiting early
    "TRIX_HOUR_OPEN":           18,                 # use trix temperature to open from this hour
    "TRIX_HOUR_CLOSE":          19,                 # revert back to normal threshold from this hour
    "TEMP_LED":                 24,
    "SERVOS": [
        {
            "NAME":             "Top",
            "GPIO":             12,                 # GPIO Numbers (BCM), which opens the windows
            "ROTATION":         270,                # most servos 180*, but 270* & 360* also valid
            "OPEN_ANGLE":       54,                 # degree, how much the servo will open the window
            "CLOSE_ANGLE":      0,                  # degree, how much the servo will close the window
        }, {
            "NAME":             "Side",
            "GPIO":             13,
            "ROTATION":         270,
            "OPEN_ANGLE":       -54,
            "CLOSE_ANGLE":      0
        }],
    "SERVO_INCREMENT":          10,                 # move servo in increments for smooth motion
    "SERVO_MIN_WIDTH":          500,                # most anti-clockwise
    "SERVO_MAX_WIDTH":          2500,               # most clockwise
    "SERVO_ZERO_DEGREES":       1500,
    "EXTREME_WET":              300,                # extreme wet - average analog value of all sensors
    "EXTREME_DRY":              800,                # extreme dry - average analog value of all sensors
    "OPERATE_FROM":             7,                  # read moisture and operate windows from hour
    "OPERATE_UNTIL":            21,                 # read moisture and operate windows until hour
    "PUMP": 
        {
            "LED_GPIO":         22,
            "GPIO":             23,                 # GPIO Number (BCM) for the Relay"
            "WATERING_FACTOR":  75,                 # Calculate seconds pump should be turned on based on moisture reading, higher means less water
            "WATERING_TIME":    7,                  # Seconds, default pump should be turned on
            "MIN_WATER":        4                   # Seconds, minimum pump should be turned on
        },
    "SENSORS": [
        {
            "NAME":             "Green",
            "MOISTURE_CHANNEL": 1,                  # of MCP3008
            "LED":              16
        }, {
            "NAME":             "Blue",
            "MOISTURE_CHANNEL": 2,                  # of MCP3008
            "LED":              25
        }, {
            "NAME":             "Yellow",
            "MOISTURE_CHANNEL": 3,                  # of MCP3008
            "LED":              17
        }, {
            "NAME":             "White",
            "MOISTURE_CHANNEL": 4,                  # of MCP3008
            "LED":              19

        }],
    "BUTTON_REBOOT":            6,
    "BUTTON_WATER":             26
}
