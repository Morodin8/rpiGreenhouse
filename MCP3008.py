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
    value += v
    print("readings: {}, average: {}".format(log, value))
    return value

def readMoisture(pi):
    try:
        total = 0.0
        adc = pi.spi_open(0, 1e6) # CE0
        
        for sensor in SETTINGS["SENSORS"]:
            value = readSensor(pi, adc, sensor)
    
            if value is not None:
                total += value
                if value > SETTINGS["EXTREME_DRY"]:
                    utils.blinkLed(pi, sensor["LED"], 10, 0.2)
                    print("too dry\n")
                elif value < SETTINGS["EXTREME_WET"]:
                    print("too wet\n")
                    pi.set_mode(sensor["LED"], pigpio.OUTPUT)
                    pi.write(sensor["LED"], 1)
                else:
                    print("Moisture just right\n")
                    pi.set_mode(sensor["LED"], pigpio.OUTPUT)
                    pi.write(sensor["LED"], 0)
                    
            else:
                # failed to get moisture reading
                return 0

        return (total / float(len(SETTINGS["SENSORS"])))
   
    finally:
        pi.spi_close(adc)
