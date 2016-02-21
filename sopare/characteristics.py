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

import globalvars

class characteristic:

    def __init__(self, debug):
        self.debug = debug

    def getcharacteristic(self, fft, tendency):
        fft = [abs(i) for i in fft]
        fft_len = 0
        chunked_fft_avg = [ ]
        chunked_fft_max = [ ]
        steps = 50
  
        for i in range(0, len(fft), steps):
            chunk_avg = sum(fft[i:i+steps])/steps
            chunked_fft_avg.append(int(abs(chunk_avg)))
            chunked_fft_max.append(int(max(fft[i:i+steps])))

        fft_len = len(chunked_fft_avg)
        right_trim = fft_len
        for i in range(len(chunked_fft_avg)-1, 0, -1):
            if (chunked_fft_avg[i] == 0 and right_trim == i + 1):
                right_trim = i

        if (right_trim > len(globalvars.IMPORTANCE)):
            right_trim = len(globalvars.IMPORTANCE)

        if (right_trim < len(chunked_fft_avg)):
            chunked_fft_max = chunked_fft_max[0:right_trim]
            chunked_fft_avg = chunked_fft_avg[0:right_trim]

        # We return nothing if the fft_len is below 15 as it is useless  
        if (fft_len <= 15):
            return None

        tendency_characteristic = self.get_tendency(tendency)

        fft_approach = self.get_approach(chunked_fft_max)
        model_characteristic = {'fft_freq': fft_len , 'fft_approach': fft_approach, 'fft_avg': chunked_fft_avg, 'tendency': tendency_characteristic }

        return model_characteristic

    def get_approach(self, data):
        data = [abs(i) for i in data]
        ld = len(data)
        result = [ld] * ld
        m = max(data)+1
        l = 0
        pos = 0
        for z in range(0, ld):
            pos = z
            for i, a in enumerate(data):
                if (a < m and a > l):
                    l = a
                    pos = i
            result[pos] = z
            m = l
            l = 0
        return result

    def get_tendency(self, data):
        peaks = 0
        avg = (sum(data)/len(data))
        delta = data[0]-data[len(data)-1]
        lowercut = avg*1.1
        high = 0
        for n in data:
            if (n > high):
                high = n
            elif (n < lowercut):
                if (high > lowercut):
                    peaks += 1
                high = 0
        tendency = { 'len': len(data), 'peaks': peaks, 'avg': avg, 'delta': delta }
        return tendency
  
    def get_word_tendency(self, data):
        if (len(data) == 0):
            return None
        peaks = 0
        maxi = max(data)
        if (maxi < 100000):
            return None
        high = int(maxi * .6)
        low = high / 2
        fly_high = True
        for n in data:
            if (n > high and fly_high):
                peaks += 1
                fly_high = False
            if (n < low):
                fly_high = True
        word_tendency = { 'peaks': peaks, 'max': maxi }
        return word_tendency
            
