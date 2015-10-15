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

import difflib
import util

class analyze():

 MIN_RATIO = .6
 MIN_SIMILARITY = 60
 CONVERGENCY = .5

 def __init__(self, debug):
  self.debug = debug
  self.util = util.util(debug, None)
  self.DICT = self.util.getDICT()
  self.reset()

 def reset(self):
  self.first_approach = [ ]

 def get_best_results(self):
  best_results = [ ]
  best_bets = [ ]
  for elements in self.first_approach:
   stringify = [ ]
   for i,e in  enumerate(elements):
    dict = e['dict']
    sim = e['similarity']
    stringify.append(dict)
   best_bets.append(stringify) 

  if (self.debug):
   print best_bets

  print best_bets

  return best_results
   
 def compare(self, counter, characteristic):
  fft_freq = characteristic['fft_freq']
  fft_avg = characteristic['fft_avg']
  tendency = characteristic['tendency']
  sm = difflib.SequenceMatcher(None, fft_freq, [])
  sm2 = difflib.SequenceMatcher(None, tendency, [])
  avg_similarity = 0

  guess_results = [ ]

  for dict_entries in self.DICT['dict']:
   dict_characteristic = dict_entries['characteristic']
   dict_fft_freq = dict_characteristic['fft_freq']
   dict_fft_avg = dict_characteristic['fft_avg']
   dict_tendency = dict_characteristic['tendency']
   dict = dict_entries['id']
   sm.set_seq2(dict_fft_freq)
   sm2.set_seq2(dict_tendency)
   freq_ratio = sm.ratio()
   tendency_ratio = sm2.ratio()
   if (freq_ratio > analyze.MIN_RATIO):
    avg_similarity = self.compare_avg(fft_freq, fft_avg, dict_fft_freq, dict_fft_avg)
    if (avg_similarity > analyze.MIN_SIMILARITY):
     guess = { 'dict': dict, 'similarity': avg_similarity*tendency_ratio, 'pos': counter}
     guess_results.append(guess)
  if (len(guess_results) > 0):
   self.first_approach.append(guess_results)

 def compare_avg(self, fft_freq, fft_avg, dict_fft_freq, dict_fft_avg):
  c_similarities = [ ]
  d_similarities = [ ]
  found = 0
  for i, ff in enumerate(fft_freq):
   if (ff in dict_fft_freq):
    ds_pos = dict_fft_freq.index(ff)
    c_similarities.append(i)
    d_similarities.append(ds_pos)

  for i in range(0,len(c_similarities)):
   a = fft_avg[c_similarities[i]]
   b = dict_fft_avg[d_similarities[i]]
   if (a==b or ( (a + (a*analyze.CONVERGENCY))  > b and (a - (a*analyze.CONVERGENCY)) < b)):
    found +=1
  
  return found*100/len(c_similarities)
   
  
