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
import MCP3008
import pigpio
import time

pi = pigpio.pi()

def measureMoisture():
    pump = SETTINGS["PUMP"]

    try:
        average = MCP3008.readMoisture(pi)
    except:
        average = 0
        
    if average > 0:
        average = round(average, 2)
        wateringTime = round(average / pump["WATERING_FACTOR"], 2)
        
        if wateringTime < pump["MIN_WATER"]:
            print("Watering time, {}, too low. Use minimum watering time: {}".format(wateringTime, pump["MIN_WATER"]))
            wateringTime = pump["MIN_WATER"]
    else:
        wateringTime = pump["WATERING_TIME"]
        print("Failed to get moisture reading, use default watering time {}".format(wateringTime))
        for sensor in SETTINGS["SENSORS"]:
            utils.blinkLed(pi, sensor["LED"], 20, 0.2)
    
    # turn pump on for some seconds
    print("{}: moisture: {} - turn pump on for {} seconds".format(timestamp, average, wateringTime))
    pi.set_mode(pump["LED_GPIO"], pigpio.OUTPUT)
    pi.set_mode(pump["GPIO"], pigpio.OUTPUT)
    pi.write(pump["LED_GPIO"], 1)
    pi.write(pump["GPIO"], 0)
    time.sleep(wateringTime)
    pi.write(pump["GPIO"], 1)
    pi.write(pump["LED_GPIO"], 0)       

if __name__ == "__main__":
    try:
        timestamp = utils.readTime()
        print("\n>>>>>>>>>> {} waterPlants started >>>>>>>>>>".format(timestamp))
        # execute functions
        measureMoisture()

        timestamp = utils.readTime()
        print("<<<<<<<<<< {} waterPlants ended <<<<<<<<<<\n".format(timestamp))
    
    finally:
        print("clean up PIG")
        pi.stop()
