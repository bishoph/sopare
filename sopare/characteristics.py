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

import config
import math
import heapq
import util

class characteristic:

    def __init__(self, debug):
        self.debug = debug

    def getcharacteristic(self, fft, tendency, meta):
        fft = fft[config.LOW_FREQ:config.HIGH_FREQ]
        fft = [abs(i) for i in fft]
        fft_len = 0
        chunked_fft_max = [ ]
        last = 0
        progessive = 1
        i = 0
        while (i < len(fft)):
            if (hasattr(config, 'START_PROGRESSIVE_FACTOR')  and i >= config.START_PROGRESSIVE_FACTOR):
                progessive += progessive*config.PROGRESSIVE_FACTOR
            else:
                progessive = config.MIN_PROGRESSIVE_STEP
            if (progessive < config.MIN_PROGRESSIVE_STEP):
                progessive = config.MIN_PROGRESSIVE_STEP
            if (progessive > config.MAX_PROGRESSIVE_STEP):
                progessive = config.MAX_PROGRESSIVE_STEP
            last = i
            i += int(progessive)
            chunked_fft_max.append(int(sum(fft[last:i])))
            
        fft_len = len(chunked_fft_max)
        max_max = max(chunked_fft_max)

        # return None for useless stuff
        if (fft_len <= config.MIN_FFT_LEN or max_max < config.MIN_FFT_MAX): 
            return None

        tendency_characteristic = self.get_tendency(tendency)
        if (tendency_characteristic == None):
            return None

        fft_max, fft_outline = self.get_outline(chunked_fft_max, len(chunked_fft_max))
        token_peaks = self.get_token_peaks(meta)
        model_characteristic = {'fft_freq': fft_len , 'fft_max': fft_max, 'fft_outline': fft_outline, 'tendency': tendency_characteristic, 'token_peaks': token_peaks }
        return model_characteristic

    def get_token_peaks(self, meta):
        token_peaks = [ ]
        for m in meta:
            if ('token_peaks' in m):
                return m['token_peaks']
        return token_peaks

    def get_highest(self, arr, n):
        return heapq.nlargest(n, arr)

    def get_outline(self, arr, n):
        high5 = self.get_highest(arr, n)
        high5i = [ ]
        highoutline = [ ]
        highv = high5[0] / config.GET_HIGH_THRESHOLD
        for h in high5:
            if (h >= highv):
                i = arr.index(h)
                high5i.append(i)
                alpha = math.degrees(math.atan( h / ((i+1.0) * (i+1)*512) ))
                highoutline.append(alpha)
            else:
                i = arr.index(h)
                high5i.append(i)
                arr[i] = 0
        return arr, highoutline

    def get_tendency(self, data):
        ll = len(data)
        if (ll == 0):
            return None
        peaks = 0
        avg = (sum(data)/ll)
        delta = data[0]-data[ll-1]
        lowercut = avg*1.1
        high = 0
        highest = 0
        pos = 0
        hpos = 0
        for n in data:
            if (n > high):
                high = n
                highest = high
                hpos = pos
            elif (n < lowercut):
                if (high > lowercut):
                    peaks += 1
                high = 0
            pos += 1
        if (hpos == 0):
            return None
        e = highest/(hpos*512.0)
        alpha = math.degrees(math.atan(e))
        tendency = { 'len': ll, 'deg': alpha, 'avg': avg, 'delta': delta }
        return tendency
  
    def get_word_tendency(self, peaks, characteristics):
        ll = len(peaks)
        if (ll == 0 or len(characteristics) > 20): # TODO: Make configurable
            if (self.debug):
                print ('ignoring get_word_tendency as we got '+str(ll) + ' characteristics' )
            return None
        peakavg = sum(peaks)/ll
        highpeak = 0
        peakpos = 0
        lowpeak = 0
        lowpos = 0
        up = 0
        gotcha = False
        start_end_pos = [ ]
        high_pos = [ ]
        first = True
        for i, peak in enumerate(peaks):
            if (peak > highpeak):
                highpeak = peak
                if (peak > peakavg):
                    peakpos = i
                    if (first):
                        first = False
                        start_end_pos.append(i)
                lowpeak = peak / 2
                if (gotcha):
                    up += 1
                    if ((up > 2 and peak > peakavg) or i == len(peaks)-1):
                        gotcha = False
                        start_end_pos.append(lowpos)
            else:
                if (peak < lowpeak):
                    if (peakpos not in high_pos):
                        high_pos.append(peakpos)
                        start_end_pos.append(i)
                    lowpeak = peak
                    lowpos = i
                    highpeak = peak * 2
                    up = 0
                    gotcha = True
        if (len(peaks) not in start_end_pos):
            start_end_pos.append(len(peaks))

        start_pos = [ ]
        peak_length = [ ]
        peak_pos = [ ]
        for hpos in high_pos:
            for a in range(0, len(start_end_pos)-1, 1):
                if (hpos > start_end_pos[a] and hpos < start_end_pos[a+1]):
                    start_pos.append(start_end_pos[a])
                    peak_length.append(start_end_pos[a+1] - start_end_pos[a])
        fft_shape = [ ]
        for c in characteristics:
            characteristic, meta = c
            if (characteristic != None):
                fft_shape.extend(characteristic['fft_max'])
        word_tendency = { 'peaks': len(start_pos), 'start_pos': start_pos, 'peak_length': peak_length, 'shape': peaks, 'fft_shape': fft_shape }
        return word_tendency            

