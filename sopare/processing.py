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

import audioop
import time
import prepare
import io
import buffering

class processor:

 MAX_SLILENCE_AFTER_START = 3
 MAX_TIME = 6
 TOKEN_IDENTIFIER = 5

 def __init__(self, endless_loop, debug, plot, wave, outfile, dict, buffering, THRESHOLD = 500, live = True):
  self.append = False
  self.endless_loop = endless_loop
  self.debug = debug
  self.plot = plot
  self.wave = wave
  self.out = None
  if (outfile != None):
   self.out = io.open(outfile, 'wb')
  self.buffering = buffering
  self.dict = dict
  self.THRESHOLD = THRESHOLD
  self.live = live
  self.timer = 0
  self.silence_timer = 0
  self.silence_counter = 0
  self.silence_buffer = [ ]
  self.prepare = prepare.preparing(debug, plot, wave, dict)

 def stop(self, message, timeout):
  if (self.debug):
   print (message)
  if (self.out != None):
   self.out.close()
  self.append = False
  self.silence_timer = 0
  if (self.endless_loop == False):
   self.prepare.stop()
  else:
   self.prepare.filter_reset()
   self.prepare.reset()
  if (self.buffering != None):
   self.buffering.stop()

 def check_silence(self, buf):
  volume = audioop.rms(buf, 2)
  if (volume > self.THRESHOLD):
   if (self.append == False):
    if (self.debug):
     print ('starting append mode')
    self.silence_timer = time.time()
    self.timer = time.time()
    for sbuf in self.silence_buffer:
     self.prepare.prepare(sbuf, volume)
    self.silence_buffer = [ ]
   self.append = True
   self.silence_counter = 0
  else:
   self.silence_counter += 1
   self.silence_buffer.append(buf)
   if (len(self.silence_buffer) > 3):
    del self.silence_buffer[0]
  if (self.out != None and self.out.closed != True):
   self.out.write(buf)
  if (self.append == True):
   self.prepare.prepare(buf, volume)
  if (self.append == True and self.silence_timer > 0 and self.silence_timer + processor.MAX_SLILENCE_AFTER_START < time.time() and self.live == True and self.endless_loop == False):
   self.stop("stop append mode because of silence", True)
  if (self.append == True and self.timer + processor.MAX_TIME < time.time() and self.live == True and self.endless_loop == False):
   self.stop("stop append mode because time is up", False)
  if (self.append == True and self.live == True and self.endless_loop == True and self.silence_counter > 300):
   self.append = False
   self.stop("endless loop silence detected", True)
   
