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
if len(sys.argv) == 3:
    windowThreshold = sys.argv[1].split(',')
    fanThreshold = sys.argv[2]
else:
    windowThreshold = SETTINGS["WINDOW_THRESHOLD"]
    fanThreshold = SETTINGS["FAN_THRESHOLD"]

pi = pigpio.pi()

def measureMoisture():
    if SETTINGS["OPERATE_FROM"] <= timestamp.hour < SETTINGS["OPERATE_UNTIL"]:
        average = MCP3008.readMoisture(pi)

        if average == 0:
            utils.turnOffLeds(pi)
            print("Failed to get moisture reading!\n")

        return average
    else:
        utils.turnOffLeds(pi)
        return 0
    
def operateWindow(isClose, servo):
    if not pi.connected:
        print("Failed to connect to pigpio. Leaving window\n")
        return

    if isClose:
        angle = servo["CLOSE_ANGLE"]
    else:
        angle = servo["OPEN_ANGLE"]
        
    print("{} GPIO: {}, Angle: {}".format(servo["NAME"], servo["GPIO"], angle))
    pulseWidth = servoUtils.calcPulseWidth(angle, servo["ROTATION"])
    
    if (pulseWidth == 0):
        print("Trying to turn servo beyond it's limit, Leaving window.")
    else:
        try:
            currentWidth = float(pi.get_servo_pulsewidth(servo["GPIO"]))
            print("currentWidth: {}".format(currentWidth))
            if currentWidth == 0:
                currentWidth = servoUtils.setCurrentWidth(isClose, currentWidth, servo)

        except:
            currentWidth = servoUtils.setCurrentWidth(isClose, 0, servo)
            width = servoUtils.safeSetPulseWidth(currentWidth)
            pi.set_servo_pulsewidth(servo["GPIO"], width)
        
        if currentWidth < pulseWidth:
            inc = SETTINGS["SERVO_INCREMENT"]
        else:
            inc = SETTINGS["SERVO_INCREMENT"] * -1
        
        setWidth = currentWidth
        print("setWidth: {}, pulseWidth: {}, inc: {}".format(setWidth, pulseWidth, inc))

        while (pulseWidth > setWidth and inc > 0) or (pulseWidth < setWidth and inc < 0):    
            width = servoUtils.safeSetPulseWidth(setWidth)
            pi.set_servo_pulsewidth(servo["GPIO"], width)
            setWidth += inc
            time.sleep(0.05)
        
        print("set width to {}\n".format(pulseWidth))
        width = servoUtils.safeSetPulseWidth(pulseWidth)
        pi.set_servo_pulsewidth(servo["GPIO"], width)

def shouldCloseWindow(temperature):
    openWindow = False
    closeWindow = True

    if timestamp.hour < SETTINGS["THRESHOLD_HOUR"]:
        ampmThreshold = float(windowThreshold[0])
        print("Hour = {}. Use AM temperature: {}".format(timestamp.hour, ampmThreshold))
    else:
        ampmThreshold = float(windowThreshold[1])
        print("Hour = {}. Use PM temperature: {}".format(timestamp.hour, ampmThreshold))

    if temperature >= ampmThreshold:
        return openWindow
    else:
        if timestamp.month == SETTINGS["TRIX_MONTH"]:
            if SETTINGS["TRIX_HOUR_OPEN"] <= timestamp.hour <= SETTINGS["TRIX_HOUR_CLOSE"]:
                if temperature >= SETTINGS["TRIX_THRESHOLD"]:
                    print("trix open window temperature: {}".format(SETTINGS["TRIX_THRESHOLD"]))
                    utils.blinkLed(pi, SETTINGS["TEMP_LED"], 30, 0.1)
                    return openWindow
    
        return closeWindow

def operateFan(temperature):
    pi.set_mode(SETTINGS["FAN_GPIO"], pigpio.OUTPUT)

    if temperature < float(fanThreshold):
        print("turn fan off\n")
        pi.write(SETTINGS["FAN_GPIO"], 1)
    else:
        print("turn fan on\n")
        pi.write(SETTINGS["FAN_GPIO"], 0)

def readTemperature(retry):
    def output_data(timestamp, temperature, humidity):
        date = datetime.datetime.fromtimestamp(timestamp).replace(microsecond=0).isoformat()
        print(u"Date: {:s}, Temperature: {:g}*C, Humidity: {:g}%\n".format(date, temperature, humidity))
        return [True, date, temperature, humidity]

    def readWithRetry(retry, reads):
        override = False
        while reads > 0:
            try:
                timestamp, gpio, status, temperature, humidity = sensor.read(override)   #read DHT device
                if(status == DHT.DHT_TIMEOUT):  # no response from sensor
                    print("Error: DHT_TIMEOUT no response from sensor, retry {}".format(retry))
                    break
                if(status == DHT.DHT_GOOD):
                    return output_data(timestamp, temperature, humidity) # Return after successful read
                time.sleep(2)
                reads -=1
                if reads > 1:
                    print("Read {} failed to get a reading, retrying. Status: {}".format(reads, status))
                elif reads == 1:
                    print("Read {} failed to get reading, retrying with override. Status: {}".format(reads, status))
                    override = True
                else:
                    print("Read {} failed to get reading after retrying. Status: {}".format(reads, status))
            except KeyboardInterrupt:
                break

        if retry:
            # retry for DHT_TIMEOUT
            return readWithRetry(False, 5)

        return [False, 0, 0, 0]
    
    sensor = DHT.sensor(pi, SETTINGS["DHT_GPIO"], model = SETTINGS["DHT_SENSOR"])

    return readWithRetry(True, 5)

def regulateTemperature():
    if SETTINGS["OPERATE_FROM"] <= timestamp.hour < SETTINGS["OPERATE_UNTIL"]:
        print("DHT_SENSOR: {}, DHT_GPIO: {}, WINDOW_THRESHOLD: {}, FAN_THRESHOLD: {}".format(SETTINGS["DHT_SENSOR"], SETTINGS["DHT_GPIO"], windowThreshold, fanThreshold))
        # read temperature, set retry to true to try twice    
        valid, date, temperature, humidity = readTemperature(True)

        if valid:
            for servo in SETTINGS["SERVOS"]:
                if shouldCloseWindow(temperature):
                    # close window
                    print("close window - {}".format(servo["NAME"]))
                    utils.blinkLed(pi, SETTINGS["TEMP_LED"], 10, 0.2)
                    operateWindow(True, servo)
                else:
                    # open window
                    print("open window - {}".format(servo["NAME"]))
                    utils.blinkLed(pi, SETTINGS["TEMP_LED"])
                    operateWindow(False, servo)

            operateFan(temperature)
            return temperature
                    
        else:
            print("Failed to get reading. Leaving window & fan\n")
            pi.set_mode(SETTINGS["TEMP_LED"], pigpio.OUTPUT)
            pi.write(SETTINGS["TEMP_LED"], 1)

    elif timestamp.hour == SETTINGS["OPERATE_UNTIL"]:
        # close window
        for servo in SETTINGS["SERVOS"]:
            print("close window for the night {}".format(servo["NAME"]))
            utils.blinkLed(pi, SETTINGS["TEMP_LED"], 10, 0.2)
            operateWindow(True, servo)

        operateFan(0)
        # turn fan off ...
        print("...for the night")
        utils.turnOffLeds(pi)
    
    return 0

if __name__ == "__main__":
    try:
        timestamp = utils.readTime()
        print("\n>>>>>>>>>> {} greenhouse started >>>>>>>>>>".format(timestamp))
        # execute functions
        temperature = regulateTemperature()
        moisture = measureMoisture()

        print(u"timestamp: {}, temperature: {:g}*C, moisture: {}".format(timestamp, temperature, moisture))
        timestamp = utils.readTime()
        print("<<<<<<<<<< {} greenhouse ended <<<<<<<<<<\n".format(timestamp))
    
    finally:
        print("clean up PIG") 
        pi.stop()
