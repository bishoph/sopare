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
import filter

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
  self.reset()
  self.plot_buffer = [ ]

 def tokenize(self, meta):
  if (len(self.buffer) > 0 and self.last_token_start < len(self.buffer)):
   if (self.debug):
    print ('token: '+str(self.last_token_start) +':'+str(len(self.buffer)))
   self.filter.filter(self.buffer[self.last_token_start:len(self.buffer)], meta)
   self.buffer = [ ]
   self.last_token_start = 0

 def stop(self):
  self.tokenize([{ 'token': 'stop' }])
  self.filter.stop()
  if (self.plot):
   self.visual.create_sample(self.plot_buffer, 'sample.png')
  self.filter_reset()
  self.reset()

 def reset(self):
  self.counter = 0
  self.silence = 0
  self.token_start = False
  self.min_token_length = 0
  self.min_word_length = 0
  self.new_token = False
  self.last_token_start = 0
  self.token_counter = 0
  self.last_dmax = 0
  self.last_adaptive = 0
  self.adaptive = 0
  self.word_zoning = 0
  self.entered_silence = False
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
  new_word = False
  meta = [ ]

  if (cur_sum < 100000):
   self.word_zoning += 1
  else:
   self.word_zoning = 0   

 
  # long silence indicates -> new word
  if (self.silence == 20 and self.new_token == False and self.token_start == False and self.min_word_length > 10):
   new_word = True
   meta.append({ 'token': 'silence', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })

  # signal drop is most likely -> new word
  if (self.word_zoning >= 10 and self.min_word_length >= 40):
   new_word = True
   meta.append({ 'token': 'zoning', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })

  # rise after descent, min word length to not start to early -> new word
  if (dmax > self.last_dmax and self.adaptive > self.last_adaptive and self.new_token == True and self.token_start == True and self.silence < 20 and self.min_word_length > 50):
   new_word = True
   print ('rise after descent')
   meta.append({ 'token': 'rise after descent', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })

  self.last_dmax = dmax
  self.last_adaptive = self.adaptive

  # silence / token end
  if (self.adaptive < preparing.PITCH or volume < preparing.PITCH or dmax < preparing.PITCH):
   self.silence += 1
   if (self.silence == 10 and self.new_token == False and self.min_token_length >= preparing.MIN_TOKEN_LENGTH):
    new_word = True    
    meta.append({ 'token': 'silence/token end', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })
   if (self.silence > 30):
    if (self.entered_silence == False):
     new_word = True
     meta.append({ 'token': 'long silence', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })
    self.entered_silence = True
  else:
   self.entered_silence = False
  
  # pitch / token end 
  if (volume < preparing.PITCH and self.new_token == False and self.token_start == True and self.min_token_length >= preparing.MIN_TOKEN_LENGTH and new_word == False):
   self.silence = 0
   self.new_token = True 
   self.token_start = False
   meta.append({ 'token': 'pitch/token end', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })

  # pitch / token start
  elif (self.adaptive > preparing.PITCH_START or volume > preparing.PITCH_START and self.new_token == True and self.token_start == False and new_word == False):
   self.token_start = True
   self.silence = 0
   meta.append({ 'token': 'pitch/token start', 'silence': self.silence, 'word_length': self.min_word_length, 'zoning': self.word_zoning, 'adapting': self.adaptive, 'volume': volume })

  if ((self.new_token == True and self.silence < 10) or new_word == True):
   self.new_token = False
   self.token_counter += 1
   self.min_token_length = 0
   self.adaptive = 0
   self.tokenize(meta)
   if (new_word == True):
    self.min_word_length = 0
