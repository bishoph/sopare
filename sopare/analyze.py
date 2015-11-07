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

class analyze():

 MIN_SIMILARITY = 40

 def __init__(self, debug):
  self.debug = debug
  self.util = util.util(debug, None)
  self.DICT = self.util.getDICT()
  self.reset()

 def reset(self):
  self.first_approach = [ ]

 def get_best_results(self):
  print self.first_approach
  return self.first_approach
   
 def compare(self, counter, characteristic):
  for dict_entries in self.DICT['dict']:
   if (self.debug):
    print ('comparing characteristic against '+dict_entries['id'])
   dict_characteristic = dict_entries['characteristic']
   characteristic_tokens = dict_characteristic['tokens']
   for token in characteristic_tokens:
    guess = self.compare_token(characteristic['fft_min'], characteristic['fft_max'], token['fft_min_min'], token['fft_min_max'], token['fft_max_min'], token['fft_max_max'])
    convergency = self.compare_tendency(characteristic, token)
    match = guess + convergency
    if (match > analyze.MIN_SIMILARITY):
     self.first_approach.append((dict_entries['id'], token['num'], counter, guess, convergency))

 def compare_tendency(self, characteristic, token):
  convergency = 0
  if (characteristic['fft_freq'] >= token['fft_freq_min'] and characteristic['fft_freq'] <= token['fft_freq_min']):
   convergency += 10 
  if (characteristic['tendency']['len'] >= token['tendency']['len_min'] and characteristic['tendency']['len'] <= token['tendency']['len_max']):
   convergency += 10
  if (characteristic['tendency']['peaks'] >= token['tendency']['peaks_min'] and characteristic['tendency']['peaks'] <= token['tendency']['peaks_max']):
   convergency += 10
  return convergency
  

 def compare_token(self, fft_min, fft_max, fft_min_min, fft_min_max, fft_max_min, fft_max_max):
  zipped = zip(fft_min, fft_max, fft_min_min, fft_min_max, fft_max_min, fft_max_max)
  match = 0
  for z in zipped:
   a, b, c, d, e, f = z
   if (a >= c and a <= d and b >= e and b <= f):
    match += 1
  guessing = match*100/len(zipped)    
  return guessing
   
  
