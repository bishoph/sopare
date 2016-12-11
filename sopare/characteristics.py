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

import numpy
import config

class characteristic:

    def __init__(self, debug):
        self.debug = debug

    def getcharacteristic(self, fft, meta):
        fft = fft[config.LOW_FREQ:config.HIGH_FREQ]
        fft = numpy.abs(fft)
        chunked_fft_max = [ ]
        progessive = 1
        i = config.MIN_PROGRESSIVE_STEP
        for x in range(0, len(fft), i):
            if (hasattr(config, 'START_PROGRESSIVE_FACTOR')  and x >= config.START_PROGRESSIVE_FACTOR):
                progessive += progessive * config.PROGRESSIVE_FACTOR
                i += int(progessive)
                if (i > config.MAX_PROGRESSIVE_STEP):
                    i = config.MAX_PROGRESSIVE_STEP
            chunked_fft_max.append(int(sum(fft[x:x+i])))    
        df = numpy.argmax(fft)
        dfm = int(numpy.amax(fft))
        where_range = dfm / config.PEAK_FACTOR
        npeaks = numpy.array(numpy.where(fft > where_range))
        peaks = [ ]
        peaksm = [ ]
        if (npeaks.size > 0):
            peaks = [ ]
            peaksm = [ ]
            for peak in numpy.nditer(npeaks):
                peaks.append(int(peak))
                peaksm.append(int(fft[peak]))
        token_peaks = self.get_token_peaks(meta)
        volume = self.get_volume(meta)
        model_characteristic = {'df': df, 'dfm': dfm, 'peaks': peaks, 'fft_max': peaksm, 'token_peaks': token_peaks, 'volume': volume }
        return model_characteristic

    @staticmethod
    def get_token_peaks(meta):
        token_peaks = [ ]
        for m in meta:
            if ('token_peaks' in m):
                return m['token_peaks']
        return token_peaks

    @staticmethod
    def get_volume(meta):
        volume = 0
        for m in meta:
            if ('volume' in m):
                return m['volume']
        return volume
