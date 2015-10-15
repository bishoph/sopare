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
from scipy.io.wavfile import write

import multiprocessing 
import condense
import util
import visual
import analyze
import characteristics
import uuid

class worker(multiprocessing.Process):

 def __init__(self, queue, debug, plot, dict, wave):
  multiprocessing.Process.__init__(self, name="worker for prepared queue")
  self.queue = queue
  self.debug = debug
  self.plot = plot
  self.dict = dict
  self.wave = wave
  self.visual = visual.visual()
  self.condense = condense.packing()
  self.util = util.util(debug, None)
  self.analyze = analyze.analyze(debug)
  self.characteristic = characteristics.characteristic(debug)
  self.running = True
  self.reset()
  self.DICT = self.util.getDICT()
  self.start()

 def reset(self):
  self.do_analysis()
  self.counter = 0
  self.rawbuf = [ ]
  self.rawfft = [ ]
  self.raw = [ ]
  self.fft = [ ]
  self.character = [ ]
  self.uid = str(uuid.uuid4())
  self.analyze.reset()

 def do_analysis(self):
  best_results = self.analyze.get_best_results()

 def run(self):
  if (self.debug):
   print ("worker queue runner started")
  while self.running:
   obj = self.queue.get()
   if (obj['action'] == 'data'):
    raw_token = obj['token']
    self.rawbuf.extend(raw_token)
    fft = obj['fft']
    self.rawfft.extend(fft)
    raw_token_compressed = self.condense.compress(raw_token)
    raw_tendency = self.condense.model_tendency(raw_token_compressed)

    characteristic = self.characteristic.getcharacteristic(fft, raw_tendency)
    if (self.debug):
     print ('characteristic = ' + str(self.counter) + ' ' + str(characteristic))    

    if (self.dict != None):
     self.character.append( characteristic )

    if (characteristic != None):
     self.analyze.compare(self.counter, characteristic)

    if (self.wave):
     scaled = numpy.int16(raw_token/numpy.max(numpy.abs(raw_token)) * 32767)
     write('tokens/token'+str(self.counter)+self.uid+'.wav', 44100, scaled) 

    if (self.plot):
     self.visual.create_sample(raw_tendency, 'token'+str(self.counter)+'.png')
     self.visual.create_sample(fft, 'fft'+str(self.counter)+'.png')
    self.counter += 1
   elif (obj['action'] == 'reset'):
    self.reset()
   elif (obj['action'] == 'stop'):
    self.do_analysis()
    self.running = False

  if (self.dict != None):  
   if (len(self.dict) == len(self.character)):
    n = 0
    for c in self.character:
     if (c != None):
      dict_id = self.dict[n:n+1]
      self.DICT = self.util.add2dict(c, dict_id) 
      n += 1
   else:
    for c in self.character:
     if (c != None):
      self.DICT = self.util.add2dict(c, self.dict)

  if (self.wave):
   scaled = numpy.int16(self.rawbuf/numpy.max(numpy.abs(self.rawbuf)) * 32767)
   write('tokens/filtered_results.wav', 44100, scaled)
  self.queue.close()

  if (self.plot):
   self.visual.create_sample(self.rawfft, 'fft.png')
