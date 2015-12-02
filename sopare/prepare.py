#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Martin Kauss (yo@bishoph.org)

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

 def tokenize(self):
  if (len(self.buffer) > 0 and self.last_token_start < len(self.buffer)):
   if (self.debug):
    print ('token: '+str(self.last_token_start) +':'+str(len(self.buffer)))
   self.filter.filter(self.buffer[self.last_token_start:len(self.buffer)])
   self.last_token_start = len(self.buffer)

 def stop(self):
  self.tokenize()
  self.filter.stop()
  if (self.plot):
   self.visual.create_sample(self.buffer, 'sample.png')
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
  self.buffer = [ ]

 def filter_reset(self):
  if (self.token_counter > 0):
   self.filter.reset()
  
 def prepare(self, buf, volume):
  data = numpy.fromstring(buf, dtype=numpy.int16)
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

  if (cur_sum < 100000):
   self.word_zoning += 1
  else:
   self.word_zoning = 0   

  # we need also a max. length of a word until we cut it out!
  if (self.min_word_length > 50):
    new_word = True
    #print ('TOO LONG ' + str(len(self.buffer)))

  # long silence indicates -> new word
  if (self.silence > 40 and self.new_token == True and self.token_start == True and self.min_word_length > 10):
   new_word = True
   #print ('SILENCE ' + str(len(self.buffer)))

  # signal drop is most likely -> new word
  if (self.word_zoning >= 10 and self.dict == None):
   new_word = True
   #print ('ZONING ' + str(len(self.buffer)));

  # rise after descent, min word length to not start to early -> new word
  if (dmax > self.last_dmax and self.adaptive > self.last_adaptive and self.new_token == True and self.token_start == True and self.silence < 20 and self.min_word_length > 50 and self.dict == None):
   new_word = True
   #print ('RISE AFTER DESCENT ' + str(len(self.buffer)))

  if (new_word == True):
   if (self.debug):
    print ('potentially a new word at '+str(self.counter) + ' '+str(self.new_token) + ' ' + str(self.token_start))
   self.filter_reset()
   self.reset()
   self.min_word_length = 0

  self.last_dmax = dmax
  self.last_adaptive = self.adaptive

  if (self.new_token == True and self.silence < 10):
   self.new_token = False
   self.tokenize()
   self.token_counter += 1
   self.min_token_length = 0
   self.adaptive = 0

  # silence / token end
  if (self.adaptive < preparing.PITCH or volume < 100 or dmax < 100):
   self.silence += 1
   if (self.silence == 10 and self.new_token == False and self.min_token_length >= preparing.MIN_TOKEN_LENGTH):
    self.new_token = True
    self.token_start = False

  # pitch / token end 
  if (volume < preparing.PITCH and self.new_token == False and self.token_start == True and self.min_token_length >= preparing.MIN_TOKEN_LENGTH):
   self.slience = 0
   self.new_token = True 
   self.token_start = False

  # pitch / token start 
  if (self.adaptive > preparing.PITCH or volume > preparing.PITCH and self.new_token == True and self.token_start == False):
   self.token_start = True
   self.slience = 0
