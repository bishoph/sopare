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

 MAX_SLILENCE_AFTER_START=2
 MAX_TIME=4
 TOKEN_IDENTIFIER=5

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
  self.prepare = prepare.preparing(debug, plot, wave, dict)
  self.silence_buffer = [ ]

 def stop(self, message, timeout):
  if (self.debug > 0):
   print (message)
  if (self.out != None):
   self.out.close()
  self.append = False
  self.silence_timer = 0
  if (self.endless_loop == False):
   self.prepare.stop()
  else:
   self.prepare.done()
  if (self.buffering != None):
   self.buffering.stop()

 def check_silence(self, buf):
  current = audioop.rms(buf, 2)

  if (current > self.THRESHOLD):
   self.silence_timer = 0
   self.silence_counter = 0
   if (self.append == False):
    self.append = True
    self.timer = time.time()
    self.silence_timer = 0
    print ("starting append mode")
    if (len(self.silence_buffer) > 0 ):
     first = True
     for silence_buffer_buf in self.silence_buffer:
      self.prepare.prepare(silence_buffer_buf, first)
      if (first):
       first = False
     self.silence_buffer = [ ]
  else:
   self.silence_buffer.append(buf)
   self.silence_counter += 1
   if (len(self.silence_buffer) > 5):
    del self.silence_buffer[0]

   if (self.append == True and self.silence_timer == 0):
    self.silence_timer = time.time() + processor.MAX_SLILENCE_AFTER_START

  if (self.append == True):
   if (self.silence_counter > processor.TOKEN_IDENTIFIER):
    self.prepare.prepare(buf, True)
    self.silence_counter = 0
   else:
    self.prepare.prepare(buf, False)

   if (self.out != None and self.out.closed != True):
    self.out.write(buf)

  if (self.append == True and self.silence_timer > 0 and self.silence_timer < time.time() and self.live == True):
   self.stop("stop append mode because of silence", True)
  if (self.append == True and self.timer+processor.MAX_TIME < time.time()):
   self.stop("stop append mode because time is up", False)
