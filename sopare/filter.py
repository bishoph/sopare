#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 - 2017 Martin Kauss (yo@bishoph.org)

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
import multiprocessing
import worker
import config
import characteristics

class filtering():

    def __init__(self, debug, plot, dict, wave):
        self.debug = debug
        self.plot = plot
        self.first = True
        self.queue = multiprocessing.Queue()
        self.characteristic = characteristics.characteristic(debug)
        self.worker = worker.worker(self.queue, debug, plot, dict, wave)

    def stop(self):
        self.queue.put({ 'action': 'stop' })
        self.queue.close()
        self.queue.join_thread()

    def reset(self):
        self.queue.put({ 'action': 'reset' })

    @staticmethod
    def check_for_windowing(meta):
        for m in meta:
            if (m['token'] == 'start analysis' or m['token'] == 'silence'):
                return True
        return False

    @staticmethod
    def get_chunked_norm(nfft):
        chunked_norm = [ ]
        progessive = 1
        i = config.MIN_PROGRESSIVE_STEP
        for x in range(0, nfft.size, i):
            if (hasattr(config, 'START_PROGRESSIVE_FACTOR')  and x >= config.START_PROGRESSIVE_FACTOR):
                progessive += progessive * config.PROGRESSIVE_FACTOR
                i += int(progessive)
                if (i > config.MAX_PROGRESSIVE_STEP):
                    i = config.MAX_PROGRESSIVE_STEP
            chunked_norm.append( nfft[x:x+i].sum() )
        return numpy.array(chunked_norm)

    @staticmethod
    def normalize(fft):
        norm = numpy.linalg.norm(fft)
        if (norm > 0):
            return (fft/norm).tolist()
        return []

    def filter(self, data, meta):
        if (self.first == False or config.HANNING == False or len(data) < 3):
            fft = numpy.fft.rfft(data)
            self.first = self.check_for_windowing(meta)
        elif (self.first == True):
            hl = len(data)
            if (hl % 2 != 0):
                hl += 1
            hw = numpy.hanning(hl)
            fft = numpy.fft.rfft(data * hw)
            self.first = False
        fft[config.HIGH_FREQ:] = 0
        fft[:config.LOW_FREQ] = 0
        data = numpy.fft.irfft(fft)
        nfft = fft[config.LOW_FREQ:config.HIGH_FREQ]
        nfft = numpy.abs(nfft)
        nfft[nfft == 0] = numpy.NaN
        nfft = numpy.log10(nfft)**2
        nfft[numpy.isnan(nfft)] = 0
        nam = numpy.amax(nfft)
        if (nam > 0):
            nfft = numpy.tanh(nfft/nam)
            chunked_norm = self.get_chunked_norm(nfft)
            normalized = self.normalize(chunked_norm)
        characteristic = self.characteristic.getcharacteristic(fft, normalized, meta)
        obj = { 'action': 'data', 'token': data, 'fft': fft, 'norm': normalized, 'meta': meta, 'characteristic': characteristic }
        self.queue.put(obj)
