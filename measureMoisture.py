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

import utils
import MCP3008
import pigpio

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

if __name__ == "__main__":
    try:
        timestamp = utils.readTime()
        print("\n>>>>>>>>>> {} measureMoisture started >>>>>>>>>>".format(timestamp))
        # execute functions
        moisture = measureMoisture()
        print("moisture: {}".format(moisture))

        timestamp = utils.readTime()
        print("<<<<<<<<<< {} measureMoisture ended <<<<<<<<<<\n".format(timestamp))
    
    finally:
        print("clean up PIG")
        pi.stop()
