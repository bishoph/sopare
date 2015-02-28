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
import visual

class packing:

 def __init__(self, debug, plot):
  self.debug = debug
  self.plot = plot
  self.SLICE = 32
  self.buffer = [ ]
  self.rawbuf = [ ]
  self.visual = visual.visual()

 def getrawdata(self):
  return self.buffer[:]

 def getrawbuf(self):
  return self.rawbuf

 def reset(self):
  if (self.plot):
   self.visual.create_sample(self.buffer, 'sample.png')
  self.buffer = [ ]

 def compress(self, buf):
  self.rawbuf.append(buf)
  compressed = [ ]
  data = numpy.fromstring(buf, dtype=numpy.int16)
  current_h = 0
  current_l = 0
  c_h = 1
  c_l = 1
  h_first = False
  counter = 0
  for a in data:
   self.buffer.append(a)
   if (a > 0):
    current_h += a
    c_h += 1
    if (counter == 0):
     h_first = True
   else:
    current_l += a
    c_l += 1
   if (counter == self.SLICE):
    peak_h = float(current_h / c_h)
    peak_l = float(current_l / c_l)
    if (h_first == True):
     if (c_h > self.SLICE / 2):
      compressed.append(peak_h)
     if (c_l > self.SLICE / 2):
      compressed.append(peak_l)
    else:
     if (c_l > self.SLICE / 2):
      compressed.append(peak_l)
     if (c_h > self.SLICE / 2):
      compressed.append(peak_h)
    c_h = 1
    c_l = 1
    counter = 1
    current = 0
    current_h = 0
    current_l = 0
   else:
    counter += 1
  return compressed
  
