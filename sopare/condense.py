#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015, 2016 Martin Kauss (yo@bishoph.org)

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

class packing():

    def __init__(self):
        self.SLICE = 16

    def compress(self, data):
        compressed = [ ]
        current_h = 0
        current_l = 0
        c_h = 1
        c_l = 1
        h_first = False
        counter = 0
        for a in data:
            if (a > 0):
                current_h += a
                c_h += 1
                if (counter == 0):
                    h_first = True
            else:
                current_l += a
                c_l += 1
            if (counter == self.SLICE):
                peak_h = float(current_h / c_h)
                peak_l = float(current_l / c_l)
                if (h_first == True):
                    if (c_h > self.SLICE / 2):
                        compressed.append(peak_h)
                    if (c_l > self.SLICE / 2):
                        compressed.append(peak_l)
                else:
                    if (c_l > self.SLICE / 2):
                        compressed.append(peak_l)
                    if (c_h > self.SLICE / 2):
                        compressed.append(peak_h)
                c_h = 1
                c_l = 1
                counter = 1
                current_h = 0
                current_l = 0
            else:
                counter += 1
        return compressed
  
    def model_tendency(self, data):
        last = 0
        last_high = 0
        tendency = [ ]
        counter = 0
        for n in data:
            if (n < 0):
                n = 0 - n
            if (n >= 0 and n > last_high):
                last_high = n
            if (counter == 8):
                if (last < last_high):
                    tendency.append(int(last))
                elif (last > last_high):
                    tendency.append(int(last))
                last = last_high
                last_high = 0
                counter = 0
            else:
                counter += 1
        return tendency[1:]
