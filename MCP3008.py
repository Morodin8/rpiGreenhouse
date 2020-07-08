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
import pigpio

def read_MCP3008(pi, adc, channel):
    count, data = pi.spi_xfer(adc, [1, (8+channel)<<4, 0])
    value = ((data[1] << 8) | data[2]) & 0x3FF
    return value

def readSensor(pi, adc, sensor):
    # read 10 times to avoid measuring errors
    print("{} - MOISTURE_CHANNEL: {}".format(sensor["NAME"], sensor["MOISTURE_CHANNEL"]))

    value = 0.0
    v = 0.0
    log = []
    for i in range(10):
        m = read_MCP3008(pi, adc, sensor["MOISTURE_CHANNEL"])
        log.append(m)
        v += m
    v /= 10.0
    value += round(v, 1)
    print("readings: {} = {}".format(log, value))
    return value

def readMoisture(pi):
    try:
        failed = 0
        total = 0.0
        adc = pi.spi_open(0, 1e6) # CE0
        
        for sensor in SETTINGS["SENSORS"]:
            value = readSensor(pi, adc, sensor)
    
            if value is not None:
                total += value
                if value > SETTINGS["EXTREME_DRY"]:
                    print("too dry\n")
                    pi.set_mode(sensor["LED"], pigpio.OUTPUT)
                    utils.blinkLed(pi, sensor["LED"], 10, 0.1)
                elif value < SETTINGS["EXTREME_WET"]:
                    print("too wet\n")
                    utils.blinkLed(pi, sensor["LED"], 5, 0.5)
                else:
                    print("Moisture just right\n")

            else:
                print("failed to get moisture reading\n")
                failed += 1

        if failed == len(SETTINGS["SENSORS"]):
            return 0

        return round(total / float(len(SETTINGS["SENSORS"]) - failed), 1)
   
    finally:
        for sensor in SETTINGS["SENSORS"]:
            pi.set_mode(sensor["LED"], pigpio.OUTPUT)
            pi.write(sensor["LED"], 0)

        pi.spi_close(adc)
