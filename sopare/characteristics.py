#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 - 2018 Martin Kauss (yo@bishoph.org)

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

class characteristic:

    def __init__(self, peak_factor):
        self.peak_factor = peak_factor

    def getcharacteristic(self, fft, chunked_norm, meta):
        fft = numpy.abs(fft)
        df = numpy.argmax(fft)
        dfm = int(numpy.amax(fft))
        fc = 0
        peaks = [ ]
        if (len(chunked_norm) > 0):
            where_range = numpy.mean(chunked_norm) / self.peak_factor
            peaks = list(numpy.array(numpy.where(chunked_norm > where_range))[0])
            where_range = numpy.mean(chunked_norm)
            npeaks = numpy.array(numpy.where(chunked_norm > where_range))
            fc = round(numpy.sum(numpy.sqrt(npeaks)), 1)
        token_peaks = self.get_token_peaks(meta)
        volume = self.get_volume(meta)
        zcr =  self.get_zcr(meta)
        model_characteristic = {'df': df, 'dfm': dfm, 'fc': fc, 'zcr': zcr, 'peaks': peaks, 'token_peaks': token_peaks, 'volume': volume, 'norm': chunked_norm }
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

    @staticmethod
    def get_zcr(meta):
        zcr = 0
        for m in meta:
            if ('zcr' in m):
                return m['zcr']
        return zcr

