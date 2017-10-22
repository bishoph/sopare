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
import filter
import sopare.visual
import sopare.util
import sopare.config
import sopare.hatch

class preparing():

    def __init__(self, hatch):
        self.hatch = hatch
        self.visual = sopare.visual.visual()
        self.util = sopare.util.util(self.hatch.get('debug'))
        self.filter = sopare.filter.filtering(self.hatch)
        self.silence = 0
        self.force = False
        self.counter = 0
        self.token_start = False
        self.new_token = False
        self.new_word = False
        self.token_counter = 0
        self.buffer = [ ]
        self.peaks = [ ]
        self.token_peaks = [ ]
        self.last_low_pos = 0
        self.force = False
        self.entered_silence = False

    def tokenize(self, meta):
        if (self.valid_token(meta)):
            if (len(self.buffer) == 0):
                self.buffer = [ 0 ] * 512
            self.filter.filter(self.buffer, meta)
            self.buffer = [ ]
            self.peaks.extend(self.token_peaks)
            self.token_peaks = [ ]
            if (self.force):
                self.reset()
                self.filter_reset()

    def valid_token(self, meta):
        for m in meta:
            if (m['token'] == 'noop'):
                self.reset()
                return False
        return True

    def stop(self):
        if (self.hatch.get('plot') == True):
            self.visual.create_sample(self.hatch.get_plot_cache(), 'sample.png')
        self.tokenize([{ 'token': 'stop' }])
        self.filter.stop()
        self.filter_reset()
        self.reset()

    def reset(self):
        self.counter = 0
        self.token_start = False
        self.new_token = False
        self.new_word = False
        self.token_counter = 0
        self.buffer = [ ]
        self.peaks = [ ]
        self.token_peaks = [ ]
        self.last_low_pos = 0
        self.force = False

    def filter_reset(self):
        if (self.token_counter > 0):
            self.filter.reset()

    def force_tokenizer(self):
        self.force = True
        self.tokenize([ { 'token': 'start analysis', 'silence': self.silence, 'pos': self.counter, 'adapting': 0, 'volume': 0, 'peaks': self.peaks } ])
  
    def prepare(self, buf, volume):
        data = numpy.fromstring(buf, dtype=numpy.int16)
        if (self.hatch.get('plot') == True and self.hatch.get('endless_loop') == False):
            self.hatch.extend_plot_cache(data)
        self.buffer.extend(data)
        self.counter += 1
        abs_data = abs(data)
        adaptive = sum(abs_data)
        self.token_peaks.append(adaptive)
        meta = [ ]

        if (volume < sopare.config.THRESHOLD):
            self.silence += 1
            if (self.silence == sopare.config.LONG_SILENCE):
                self.new_word = True
                self.entered_silence = True
                self.peaks.extend(self.token_peaks)
                meta.append({ 'token': 'start analysis', 'silence': self.silence, 'pos': self.counter, 'adapting': adaptive, 'volume': volume, 'token_peaks': self.token_peaks, 'peaks': self.peaks })
                self.peaks = [ ]
            elif (self.silence > sopare.config.LONG_SILENCE):
                meta.append({ 'token': 'noop', 'silence': self.silence, 'pos': self.counter, 'adapting': adaptive, 'volume': volume })
        else:
            self.entered_silence = False
            self.silence = 0

        if (len(self.buffer) == sopare.config.CHUNKS):
            self.new_token = True
            meta.append({ 'token': 'token', 'silence': self.silence, 'pos': self.counter, 'adapting': adaptive, 'volume': volume, 'token_peaks': self.token_peaks })

        if (self.new_token == True or self.new_word == True):
            self.new_token = False
            self.token_counter += 1
            self.tokenize(meta)
            if (self.new_word == True):
                self.new_word = False
