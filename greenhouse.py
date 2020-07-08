#!/usr/bin/env python3
#encoding: utf-8

# @Morodin 14/04/2020
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

from config import SETTINGS
import utils
import servoUtils
import MCP3008
import DHT
import pigpio
import datetime
import time
import sys

# Parse command line parameters.
if len(sys.argv) == 2:
    windowThreshold = [sys.argv[1], sys.argv[1]]
    fanThreshold = sys.argv[1]
elif len(sys.argv) == 3:
    windowThreshold = sys.argv[1].split(',')
    fanThreshold = sys.argv[2]
else:
    windowThreshold = [0, 0]
    fanThreshold = SETTINGS["FAN_THRESHOLD"]

pi = pigpio.pi()

def measureMoisture():
    try:
        average = MCP3008.readMoisture(pi)
    except:
        average = 0

    if average == 0:
        utils.turnOffLeds(pi)
        print("Failed to get moisture reading!\n")
        return "not read"

    return average

def operateFan(temperature):
    pi.set_mode(SETTINGS["FAN_GPIO"], pigpio.OUTPUT)

    if temperature < float(fanThreshold):
        print("turn fan off\n")
        pi.write(SETTINGS["FAN_GPIO"], 1)
    else:
        print("turn fan on\n")
        pi.write(SETTINGS["FAN_GPIO"], 0)

def readTemperature():
    def output_data(dtStamp, temperature, humidity):
        date = datetime.datetime.fromtimestamp(dtStamp).isoformat()
        print("Date: {}, Temperature: {:g}*C, Humidity: {:g}%\n".format(date, temperature, humidity))
        return [True, date, temperature, humidity]

    def readWithRetry(reads):
        while reads > 0:
            try:
                dtStamp, gpio, status, temperature, humidity = sensor.read(reads <= 1)   #read DHT device

                if(status == DHT.DHT_GOOD):
                    return output_data(dtStamp, temperature, humidity) # Return after successful read

                time.sleep(.5)
                reads -=1

                print("Status: {} - Failed to get a reading, reads remaining: {}.".format(status, reads))
            except KeyboardInterrupt:
                break

        # Failed to get a reading
        return [False, datetime.datetime.fromtimestamp(dtStamp).isoformat(), 0, 0]

    sensor = DHT.sensor(pi, SETTINGS["DHT_GPIO"], model = SETTINGS["DHT_SENSOR"])
    return readWithRetry(SETTINGS["DHT_READS"])

def regulateTemperature():
    print("DHT_SENSOR: {}, DHT_GPIO: {}, FAN_THRESHOLD: {}".format(SETTINGS["DHT_SENSOR"], SETTINGS["DHT_GPIO"], fanThreshold))
    # read temperature, set retry to true to try twice
    valid, date, temperature, humidity = readTemperature()

    if SETTINGS["OPERATE_FROM"] <= timestamp.hour < SETTINGS["OPERATE_UNTIL"]:
        if valid:
            for servo in SETTINGS["SERVOS"]:
                if servoUtils.shouldCloseWindow(timestamp, windowThreshold, temperature, servo):
                    # close window
                    print("close window - {}".format(servo["NAME"]))
                    utils.blinkLed(pi, SETTINGS["TEMP_LED"], 10, 0.2)
                    servoUtils.operateWindow(pi, True, servo)
                else:
                    # open window
                    print("open window - {}".format(servo["NAME"]))
                    utils.blinkLed(pi, SETTINGS["TEMP_LED"])
                    servoUtils.operateWindow(pi, False, servo)

            operateFan(temperature)
        else:
            print("Failed to get reading. Leaving window & fan\n")
            pi.set_mode(SETTINGS["TEMP_LED"], pigpio.OUTPUT)
            pi.write(SETTINGS["TEMP_LED"], 1)

    elif timestamp.hour == SETTINGS["OPERATE_UNTIL"] and timestamp.minute < 10:
        # close window ...
        for servo in SETTINGS["SERVOS"]:
            print("close window - {} ...".format(servo["NAME"]))
            utils.blinkLed(pi, SETTINGS["TEMP_LED"], 10, 0.2)
            servoUtils.operateWindow(pi, True, servo)

        # turn fan off ...
        operateFan(0)
        utils.turnOffLeds(pi)
        print("...for the night")

    return [date, temperature, humidity]

if __name__ == "__main__":
    try:
        timestamp = utils.readTime()
        print("\n>>>>>>>>>> {} greenhouse started >>>>>>>>>>".format(timestamp))
        # execute functions
        date, temperature, humidity = regulateTemperature()
        moisture = measureMoisture()

        print("{}: temperature: {:g}*C, humidity {:g}%, moisture: {}".format(date, temperature, humidity, moisture))
        timestamp = utils.readTime()
        print("<<<<<<<<<< {} greenhouse ended <<<<<<<<<<\n".format(timestamp))
    
    finally:
        print("clean up PIG")
        pi.stop()
