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
import time
import datetime
import SDL_DS1307
import pigpio

def readTime():
    try:
        ds1307 = SDL_DS1307.SDL_DS1307(1, 0x57)
        return ds1307.read_datetime()
    except:
        # alternative: return the system-time:
        return datetime.datetime.now()

def blinkLed(pi, pin, x = 2, sleep = 0.5):
    print("blinkLed pin {}, {} times".format(pin, x))
    pi.set_mode(pin, pigpio.OUTPUT)
    
    for i in range(x):
        pi.write(pin, 1)
        time.sleep(sleep)
        pi.write(pin, 0)
        time.sleep(sleep)
        
def turnOffLeds(pi):
    pins = [SETTINGS["PUMP"]["LED_GPIO"]]
    pins.append(SETTINGS["TEMP_LED"])
    for sensor in SETTINGS["SENSORS"]:
        pins.append(sensor["LED"])
        
    for pin in pins:
        pi.set_mode(pin, pigpio.OUTPUT)
        pi.write(pin, 0)