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
  self.counter = 0
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
   if (self.counter == 0):
    return
   best_results = self.analyze.get_best_results()
   pre_sorted_results = { }
   for r in best_results:
    a,b,c,d = r
    if (a in pre_sorted_results):
     o = pre_sorted_results[a]
     o['f'] += 1
     o['v'] += c
     o['t'].append(b)
    else:
     pre_sorted_results[a] = { 't': [b], 'v': c, 'l': d, 'f': 1 }
   sorted_results = [ ]
   for r in pre_sorted_results:
    o = pre_sorted_results[r]
    v = o['v']
    l = o['l']
    f = o['f']
    if (self.counter >= f and self.counter <= l):
     m = l/f
     if (m > 0):
      rv = v / m
     else:
      rv = v / l
    else:
     rv = v / self.counter
    sorted_results.append((r, rv))
   sorted_results = sorted(sorted_results,key=lambda x: (-x[1],x[0]))
   if (self.debug):
    print pre_sorted_results
   if (len(sorted_results) > 0):
    print ('based on '+str(self.counter) + ' tokens we guess >> ' + str(sorted_results))

 def run(self):
  if (self.debug):
   print ("worker queue runner started")
  while self.running:
   obj = self.queue.get()
   if (obj['action'] == 'data'):
    raw_token = obj['token']
    if (self.wave):
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
   elif (obj['action'] == 'reset' and self.dict == None):
    self.reset()
   elif (obj['action'] == 'stop'):
    self.do_analysis()
    self.running = False

  for i,c in enumerate(self.character):
   if (c != None):
    if (self.debug):
     print (c)
    if (self.dict != None):  
     self.DICT = self.util.learndict(i, c, self.dict)

  if (self.wave):
   scaled = numpy.int16(self.rawbuf/numpy.max(numpy.abs(self.rawbuf)) * 32767)
   write('tokens/filtered_results.wav', 44100, scaled)
  self.queue.close()

  if (self.plot):
   self.visual.create_sample(self.rawfft, 'fft.png')
