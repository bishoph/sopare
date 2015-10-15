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

 def __init__(self, debug, plot, wave, dict):
  self.debug = debug
  self.plot = plot
  self.wave = wave
  self.dict = dict
  self.NOISE = 500
  self.reset()
  self.visual = visual.visual()
  self.util = util.util(debug, wave)
  self.filter = filter.filtering(debug, plot, dict, wave)

 def done(self):
  if (self.debug):
   print ('elements (tokens) in buffer: '+str(self.tokens))
  #if (self.wave):
  # for index, obj in enumerate(self.tokens):
  #  self.util.saverawwave('token'+str(index), obj[0], obj[1], self.rawbuf)
  self.reset()

 def stop(self):
  self.filter.stop()
  if (self.plot):
   self.visual.create_sample(self.buffer, 'sample.png')
  self.reset()

 def reset(self):
  self.avg = 0
  self.token_counter = 1
  self.last_token_start = 0
  self.chunk_counter = 0
  self.chunk_avg = 0
  self.gotdata = False
  self.gotdatacounter = 0
  self.buffer = [ ]
  self.rawbuf = [ ]
  self.tokens = [ ]  

 def prepare(self, buf, new_token):
  self.rawbuf.extend(buf)
  data = numpy.fromstring(buf, dtype=numpy.int16)
  if (new_token == True and len(self.buffer) > 0):
   if ((self.chunk_avg/self.chunk_counter) > self.NOISE):
    self.tokens.append([self.last_token_start, len(self.buffer)])
    self.filter.filter(self.buffer[self.last_token_start:len(self.buffer)], self.token_counter)
    self.token_counter += 1
    self.gotdata = True
   elif (self.gotdata and self.gotdatacounter < 2):
    self.gotdatacounter +=1
    self.tokens.append([self.last_token_start, len(self.buffer)])
    self.filter.filter(self.buffer[self.last_token_start:len(self.buffer)], self.token_counter)
    self.token_counter += 1
   else:
    self.gotdata = False
    self.gotdatacounter = 0    
    if (self.debug):
     print ('not enough variance/noise. skipping token ['+str(self.last_token_start) + ',' + str(len(self.buffer))+']')
   self.last_token_start = len(self.buffer)
   self.chunk_counter = 0
   self.chunk_avg = 0
  self.buffer.extend(data)
  dmin = min(data)
  dmax = max(data)
  ddiff = dmax-dmin
  self.chunk_counter += 1
  self.chunk_avg += ddiff

