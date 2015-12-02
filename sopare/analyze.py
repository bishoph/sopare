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

import util
from globalvars import IMPORTANCE

class analyze():

 MIN_SIMILARITY = 40
 BEST_RESULTS_MIN = 60

 def __init__(self, debug):
  self.debug = debug
  self.util = util.util(debug, None)
  self.DICT = self.util.getDICT()
  self.reset()

 def reset(self):
  self.first_approach = { }

 def get_best_results(self):
  best_resuts = [ ]
  for dict in self.first_approach:
   arr = self.first_approach[dict]
   f = 0
   p = 0
   for a in arr:
    t, n, l, g, c = a
    if (t == n):
     f += 1
     p += (g+c)
     if (self.debug):
      print dict, t, g, c, l
     best_resuts.append((dict, t, g+c, l))
  return best_resuts
   
 def compare(self, counter, characteristic):
  for dict_entries in self.DICT['dict']:
   if (self.debug):
    print ('comparing characteristic against '+dict_entries['id'])
   dict_characteristic = dict_entries['characteristic']
   characteristic_tokens = dict_characteristic['tokens']
   for token in characteristic_tokens:
    guess = self.compare_token(characteristic['fft_avg'], token['fft_avg_min'], token['fft_avg_max'])
    convergency = self.compare_tendency(characteristic, token)
    match = guess + convergency
    if (match > analyze.MIN_SIMILARITY):
     self.add2approach(dict_entries['id'], token['num'], counter, len(characteristic_tokens), guess, convergency)

 def add2approach(self, d, t, n, l, g, c):
  if (d in self.first_approach):
   o = self.first_approach[d]
   o.append((t,n,l,g,c))
  else:
   self.first_approach[d] = [(t,n,l,g,c)]
   
 def compare_tendency(self, characteristic, token):
  convergency = 0
  if (characteristic['fft_freq'] >= token['fft_freq_min'] and characteristic['fft_freq'] <= token['fft_freq_max']):
   convergency += 10 
  else:
   convergency -= 5
  if (characteristic['tendency']['len'] >= token['tendency']['len_min'] and characteristic['tendency']['len'] <= token['tendency']['len_max']):
   convergency += 50
  else:
   convergency -= 40
  if (characteristic['tendency']['peaks'] >= token['tendency']['peaks_min'] and characteristic['tendency']['peaks'] <= token['tendency']['peaks_max']):
   convergency += 15
  else:
   convergency -= 10
  if (characteristic['tendency']['avg'] >= token['tendency']['avg_min'] and characteristic['tendency']['avg'] <= token['tendency']['avg_max']):
   convergency += 30
  else:
   convergency -= 20
  if (characteristic['tendency']['delta'] >= token['tendency']['delta_min'] and characteristic['tendency']['delta'] <= token['tendency']['delta_max']):
   convergency += 5
  else:
   convergency -= 3

  return convergency
  

 def compare_token(self, fft_avg, fft_avg_min, fft_avg_max):
  zipped = zip(fft_avg, fft_avg_min, fft_avg_max)
  match = 0
  for i,z in enumerate(zipped):
   a, b, c = z
   if (a >= b and a <= c):
    factor = .1
    if (i < len(IMPORTANCE)):
     factor = IMPORTANCE[i]
    match += factor
  guessing = int(match*100/len(zipped))
  return guessing
   
  
