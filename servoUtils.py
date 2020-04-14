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

def safeSetPulseWidth(width):
    if (width < SETTINGS["SERVO_MIN_WIDTH"]):
        print("Cannot set below {}. Width: {}".format(SETTINGS["SERVO_MIN_WIDTH"], width))
        return SETTINGS["SERVO_ZERO_DEGREES"]
    elif (width > SETTINGS["SERVO_MAX_WIDTH"]):
        print("Cannot set above {}. Width: {}".format(SETTINGS["SERVO_MAX_WIDTH"], width))
        return SETTINGS["SERVO_ZERO_DEGREES"]
    else:
        return width
        
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