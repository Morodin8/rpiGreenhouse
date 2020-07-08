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
import time
import os

if __name__ == "__main__":
    pi = pigpio.pi()

    def cbfReboot(gpio, level, tick):
        print("Callback", gpio, level, tick)
        utils.turnOffLeds()
        os.system("sudo shutdown -r now")

    def cbfWater(gpio, level, tick):
        print("Callback", gpio, level, tick)
        pi.write(SETTINGS["PUMP"]["LED_GPIO"], level ^ 1)
        pi.write(SETTINGS["PUMP"]["GPIO"], level)
        utils.turnOffLeds()

    if not pi.connected:
        print("Failed to connect to pigpio.")
    else:
        try:
            pi.set_mode(SETTINGS["BUTTON_REBOOT"], pigpio.INPUT)
            pi.set_mode(SETTINGS["BUTTON_WATER"], pigpio.INPUT)
            pi.set_mode(SETTINGS["PUMP"]["LED_GPIO"], pigpio.OUTPUT)
            pi.set_mode(SETTINGS["PUMP"]["GPIO"], pigpio.OUTPUT)

            pi.set_pull_up_down(SETTINGS["BUTTON_REBOOT"], pigpio.PUD_UP)
            pi.set_pull_up_down(SETTINGS["BUTTON_WATER"], pigpio.PUD_UP)
            
            # turn pump off at boot
            pi.write(SETTINGS["PUMP"]["GPIO"], 1)

            cb1 = pi.callback(SETTINGS["BUTTON_REBOOT"], pigpio.RISING_EDGE, cbfReboot)
            cb2 = pi.callback(SETTINGS["BUTTON_WATER"], pigpio.EITHER_EDGE, cbfWater)

            while True:
                time.sleep(1.11)

        except KeyboardInterrupt:
            print("exit")
            cb1.cancel() # To cancel callback cb1.
            cb2.cancel() # To cancel callback cb2.
