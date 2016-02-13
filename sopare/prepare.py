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
import filter
import visual
import util

class preparing():
 
    PITCH = 500

    def __init__(self, debug, plot, wave, dict):
        self.debug = debug
        self.plot = plot
        self.wave = wave
        self.dict = dict
        self.visual = visual.visual()
        self.util = util.util(debug, wave)
        self.filter = filter.filtering(debug, plot, dict, wave)
        self.silence = 0
        self.reset()
        self.plot_buffer = [ ]

    def tokenize(self, meta):
        if (len(self.buffer) > 0 and (self.entered_silence == False or (self.new_word == True and self.entered_silence == True))):
            start = 0
            end = len(self.buffer)
            #if (self.debug):
            #    print ('token: ' +str(start)+ ':'+str(end))
            self.filter.filter(self.buffer[0:end], meta)
            self.buffer = [ ]

    def stop(self):
        self.peaks = [ ]
        self.tokenize([{ 'token': 'stop' }])
        self.filter.stop()
        if (self.plot):
            self.visual.create_sample(self.plot_buffer, 'sample.png')
        self.filter_reset()
        self.reset()

    def reset(self):
        self.counter = 0
        self.silence_start = 0
        self.entered_silence = False
        self.token_start = False
        self.new_token = False
        self.new_word = False
        self.token_counter = 0
        self.last_dmax = 0
        self.last_adaptive = 0
        self.word_zoning = 0
        self.buffer = [ ]
        self.peaks = [ ]   
        self.low = 0
        self.last_low_pos = 0
        self.word_pos = [ ]

    def filter_reset(self):
        if (self.token_counter > 0):
            self.filter.reset()
  
    def prepare(self, buf, volume):
        data = numpy.fromstring(buf, dtype=numpy.int16)
        if (self.plot):
            self.plot_buffer.extend(data)
        self.buffer.extend(data)
        self.counter += 1
        abs_data = abs(data)
        dmax = max(abs_data)
        adaptive = sum(abs_data)
        meta = [ ]

        self.peaks.append(volume)

        # silence
        if (volume < preparing.PITCH):
            self.silence += 1
            if (self.silence == 50 and self.entered_silence == False):
                self.new_word = True
                self.entered_silence = True
                meta.append({ 'token': 'long silence', 'silence': self.silence, 'pos': self.counter, 'adapting': adaptive, 'volume': volume, 'word_pos': self.word_pos })
                self.peaks = [ ]
        else:
            self.silence = 0
            self.entered_silence = False

        if (volume <= self.low):
            self.low = volume
            self.last_low_pos = self.counter + 1
        if (volume > self.low):
            self.low = volume
            if (self.last_low_pos not in self.word_pos and (adaptive > 80000 or dmax > 200)):
                self.word_pos.append(self.last_low_pos)
                self.new_token = True
                meta.append({ 'token': 'rise/decent', 'silence': self.entered_silence, 'pos': self.counter, 'adapting': adaptive, 'volume': volume })

        if (self.new_token == True or self.new_word == True):
            self.new_token = False
            self.token_counter += 1
            self.tokenize(meta)
            if (self.new_word == True):
                self.new_word = False
                self.word_pos = [ ]
                self.low = 0
        self.last_dmax = dmax
        self.last_adaptive = adaptive
