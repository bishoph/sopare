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

 MIN_RATIO = .3
 MIN_SIMILARITY = 85
 CONVERGENCY = 3
 MAX_LEN_DIFF = 15

 def __init__(self, debug):
  self.debug = debug
  self.util = util.util(debug, None)
  self.DICT = self.util.getDICT()
  self.differ = difflib.SequenceMatcher(None, [], [])
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
    stringify.append((dict, sim))
   best_bets.append(stringify) 

  if (self.debug):
   print best_bets

  print best_bets

  return best_results
   
 def compare(self, counter, characteristic):
  fft_freq = characteristic['fft_freq']
  #fft_avg = characteristic['fft_avg']
  fft_min = characteristic['fft_min']
  fft_max = characteristic['fft_max']
  tendency = characteristic['tendency']
  sm = difflib.SequenceMatcher(None, fft_freq, [])
  sm2 = difflib.SequenceMatcher(None, tendency, [])
  avg_similarity = 0

  guess_results = [ ]

  for dict_entries in self.DICT['dict']:
   dict_characteristic = dict_entries['characteristic']
   dict_fft_freq = dict_characteristic['fft_freq']
   dict_fft_min = dict_characteristic['fft_min']
   dict_fft_max = dict_characteristic['fft_max']
   dict_tendency = dict_characteristic['tendency']
   dict = dict_entries['id']
   sm.set_seq2(dict_fft_freq)
   sm2.set_seq2(dict_tendency)
   freq_ratio = sm.ratio()
   tendency_ratio = sm2.ratio()
   if (freq_ratio > analyze.MIN_RATIO):
    object_similarity = self.compare_object(fft_freq, fft_min, fft_max, dict_fft_freq, dict_fft_min, dict_fft_max)
    if (object_similarity > analyze.MIN_SIMILARITY):
     guess = { 'dict': dict, 'similarity': object_similarity, 'pos': counter}
     guess_results.append(guess)
  if (len(guess_results) > 0):
   self.first_approach.append(guess_results)

 def compare_object(self, fft_freq, fft_min, fft_max, dict_fft_freq, dict_fft_min, dict_fft_max):
  zipped = zip(fft_freq, fft_min, fft_max, dict_fft_min, dict_fft_max)
  l = len(zipped)
  ll = len(dict_fft_freq)
  lll = ll -l
  if (lll > analyze.MAX_LEN_DIFF):
   if (self.debug):
    print ('No match due to MAX_LEN_DIFF '+str(lll))
   return 0 # maybe we need to be more tolerant...
  matches = 0
  for z in zipped:
   fr, fmi, fma, dfmi, dfma = z
   if (fmi == dfmi or (dfmi < fmi + analyze.CONVERGENCY and fmi - analyze.CONVERGENCY < dfmi)):
    matches = matches + 1
   if (fma == dfma or (dfma < fma + analyze.CONVERGENCY and fma - analyze.CONVERGENCY < dfma)):
    matches = matches + 1
  guessing = ((matches/2)*100/l)
  return guessing
   
  
