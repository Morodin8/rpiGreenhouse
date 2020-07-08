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
import time

def operateWindow(pi, isClose, servo):
    if not pi.connected:
        print("Failed to connect to pigpio. Leaving window\n")
        return

    if isClose:
        angle = servo["CLOSE_ANGLE"]
    else:
        angle = servo["OPEN_ANGLE"]

    print("{} GPIO: {}, Angle: {}".format(servo["NAME"], servo["GPIO"], angle))
    pulseWidth = calcPulseWidth(angle, servo["ROTATION"])

    if (pulseWidth == 0):
        print("Trying to turn servo beyond it's limit, Leaving window.")
    else:
        softOperate(pi, isClose, servo, pulseWidth)
        safeSetPulseWidth(pi, servo, pulseWidth)

def shouldCloseWindow(timestamp, windowThreshold, temperature, servo):
    openWindow = False
    closeWindow = True

    if timestamp.hour < SETTINGS["THRESHOLD_HOUR"]:
        if windowThreshold[0] == 0:
            ampmThreshold = float(servo["WINDOW_THRESHOLD"][0])
        else:
            ampmThreshold = float(windowThreshold[0])
    else:
        if windowThreshold[1] == 0:
            ampmThreshold = float(servo["WINDOW_THRESHOLD"][1])
        else:
            ampmThreshold = float(windowThreshold[1])

    print("THRESHOLD_HOUR: {}, hour: {}. Use {:g}*C threshold".format(SETTINGS["THRESHOLD_HOUR"], timestamp.hour, ampmThreshold))

    if temperature >= ampmThreshold:
        return openWindow
    else:
        if timestamp.month == SETTINGS["TRIX_MONTH"]:
            if SETTINGS["TRIX_HOUR_OPEN"] <= timestamp.hour <= SETTINGS["TRIX_HOUR_CLOSE"]:
                if temperature >= SETTINGS["TRIX_THRESHOLD"]:
                    print("trix open window at{:g}*C".format(SETTINGS["TRIX_THRESHOLD"]))
                    utils.blinkLed(pi, SETTINGS["TEMP_LED"], 30, 0.1)
                    return openWindow

        return closeWindow

def softOperate(pi, isClose, servo, pulseWidth):
    try:
        currentWidth = float(pi.get_servo_pulsewidth(servo["GPIO"]))
        print("currentWidth: {}".format(currentWidth))
        if currentWidth == 0:
            currentWidth = setCurrentWidth(isClose, currentWidth, servo)

    except:
        currentWidth = setCurrentWidth(isClose, 0, servo)
        safeSetPulseWidth(pi, servo, currentWidth)

    if currentWidth < pulseWidth:
        inc = SETTINGS["SERVO_INCREMENT"]
    else:
        inc = SETTINGS["SERVO_INCREMENT"] * -1

    setWidth = currentWidth
    print("setWidth: {}, pulseWidth: {}, inc: {}\n".format(setWidth, pulseWidth, inc))

    while (pulseWidth > setWidth and inc > 0) or (pulseWidth < setWidth and inc < 0):
        safeSetPulseWidth(pi, servo, setWidth)
        setWidth += inc
        time.sleep(0.05)

def calcPulseWidth(angle, servoRotation):
    operatingWidth = (SETTINGS["SERVO_MAX_WIDTH"] - SETTINGS["SERVO_MIN_WIDTH"]) / 2
    
    if angle == 0:
        isNegative = False
        return SETTINGS["SERVO_ZERO_DEGREES"]
    elif angle < 0:
        isNegative = True
        angle = abs(angle)
    else:
        isNegative = False

    if servoRotation != 180 and servoRotation != 270 and servoRotation != 360:
        print("Servo rotation must be ether 180, 270 or 360. servoRotation = {}".format(servoRotation))
        return SETTINGS["SERVO_ZERO_DEGREES"]

    pulseWidth = round(angle * operatingWidth / (servoRotation / 2)) + SETTINGS["SERVO_ZERO_DEGREES"]
    
    if isNegative:
        pulseWidth = SETTINGS["SERVO_MAX_WIDTH"] - pulseWidth + SETTINGS["SERVO_MIN_WIDTH"]
        print("Angle is negative, modify pulseWidth: {}".format(pulseWidth))
    
    if pulseWidth < SETTINGS["SERVO_MIN_WIDTH"] or pulseWidth > SETTINGS["SERVO_MAX_WIDTH"]:
        print("You can DAMAGE a servo if you command it to move beyond its limits! pulseWidth: {}".format(pulseWidth))
        return SETTINGS["SERVO_ZERO_DEGREES"]
        
    return pulseWidth

def safeSetPulseWidth(pi, servo, width):
    if (width == SETTINGS["SERVO_OFF"]):
        print("Turning servo off")
        setWidth = SETTINGS["SERVO_OFF"]
    elif (width < SETTINGS["SERVO_MIN_WIDTH"]):
        print("Cannot set below {}. Width: {}".format(SETTINGS["SERVO_MIN_WIDTH"], width))
        setWidth = SETTINGS["SERVO_ZERO_DEGREES"]
    elif (width > SETTINGS["SERVO_MAX_WIDTH"]):
        print("Cannot set above {}. Width: {}".format(SETTINGS["SERVO_MAX_WIDTH"], width))
        setWidth = SETTINGS["SERVO_ZERO_DEGREES"]
    else:
        setWidth = width

    pi.set_servo_pulsewidth(servo["GPIO"], setWidth)
        
def setCurrentWidth(isClose, currentWidth, servo):
    if isClose:
        if (currentWidth < SETTINGS["SERVO_MIN_WIDTH"] or currentWidth > SETTINGS["SERVO_MAX_WIDTH"]):
            if servo["OPEN_ANGLE"] > 0:
                currentWidth = SETTINGS["SERVO_MAX_WIDTH"]
            else:
                currentWidth = SETTINGS["SERVO_MIN_WIDTH"]

            print("could not get currentWidth, setting to: {}".format(currentWidth))
    else:
        if (currentWidth < SETTINGS["SERVO_MIN_WIDTH"] or currentWidth > SETTINGS["SERVO_MAX_WIDTH"]):
            currentWidth = SETTINGS["SERVO_ZERO_DEGREES"]
            print("could not get currentWidth, setting to ZERO_DEGREES: {}".format(SETTINGS["SERVO_ZERO_DEGREES"]))
            
    return currentWidth