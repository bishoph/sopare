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
    PITCH_START = 700
    MIN_TOKEN_LENGTH = 10

    def __init__(self, debug, plot, wave, dict):
        self.debug = debug
        self.plot = plot
        self.wave = wave
        self.dict = dict
        self.visual = visual.visual()
        self.util = util.util(debug, wave)
        self.filter = filter.filtering(debug, plot, dict, wave)
        self.silence = 0
        #self.file = open('/tmp/test.txt','a')
        self.reset()
        self.plot_buffer = [ ]

    def tokenize(self, meta):
        if (len(self.buffer) > 0):
            start = 0
            end = len(self.buffer)
            if (self.debug):
                print ('token: ' +str(start)+ ':'+str(end))
            self.filter.filter(self.buffer[0:end], meta)
            self.buffer = [ ]

    def stop(self):
        #self.file.close()
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
        self.min_token_length = 0
        self.min_word_length = 0
        self.new_token = False
        self.new_word = 3
        self.token_counter = 0
        self.last_dmax = 0
        self.last_adaptive = 0
        self.adaptive = 0
        self.word_zoning = 0
        self.buffer = [ ]

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
        cur_sum = sum(abs_data)
        self.adaptive += cur_sum
        self.adaptive = self.adaptive / self.counter
        self.min_token_length += 1
        self.min_word_length += 1
        meta = [ ]
     
        #self.file.write(str(self.adaptive) + ', ' +str(volume) + ', ' +str(dmax) + ', ' +str(self.silence) + '\n\r')

        # silence
        if (volume < preparing.PITCH):
            self.silence += 1
            if (self.silence == 50):
                self.new_word = 0
                meta.append({ 'token': 'long silence', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })
            if (self.adaptive < preparing.PITCH and self.entered_silence == False):
                self.new_word = 3
                self.entered_silence = True
                meta.append({ 'token': 'silence/token end', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })
        else:
            self.silence = 0
            self.entered_silence = False

        #if ((self.adaptive < preparing.PITCH or volume < preparing.PITCH) and volume < preparing.PITCH and self.min_word_length > 50):
        #if (self.adaptive < preparing.PITCH and volume < preparing.PITCH):
        #    self.silence += 1
        #    if (self.silence == 10):
        #        new_word = True
        #        meta.append({ 'token': 'silence/token end', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })
        #else:
            #self.silence = 0
            # rise/decent
            #if (dmax < self.last_dmax and dmax > preparing.PITCH and self.min_token_length >= 10):
            #    self.new_token = True
            #    meta.append({ 'token': 'rise/decent', 'silence': self.entered_silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })

        if (self.new_token == True or self.new_word == 0):
            self.new_token = False
            self.token_counter += 1
            self.min_token_length = 0
            self.adaptive = 0
            self.tokenize(meta)
            if (self.new_word == 0):
                self.min_word_length = 0
                self.new_word = 3
        if (self.new_word > 0 and self.entered_silence == True):
            self.new_word = self.new_word - 1
        self.last_dmax = dmax
