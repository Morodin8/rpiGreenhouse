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
import DHT
import pigpio
import datetime
import time

pi = pigpio.pi()

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

if __name__ == "__main__":
    try:
        timestamp = utils.readTime()
        print("\n>>>>>>>>>> {} readTemperature started >>>>>>>>>>".format(timestamp))
        # execute functions
        valid, date, temperature, humidity = readTemperature()

        print("{}: temperature: {:g}*C, humidity {:g}%".format(date, temperature, humidity))
        timestamp = utils.readTime()
        print("<<<<<<<<<< {} readTemperature ended <<<<<<<<<<\n".format(timestamp))
    
    finally:
        print("clean up PIG")
        pi.stop()
