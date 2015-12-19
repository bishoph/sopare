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
import characteristics
import globalvars

class analyze():

 MIN_SIMILARITY = 40
 BEST_RESULTS_MIN = 60

 def __init__(self, debug):
  self.debug = debug
  self.util = util.util(debug, None)
  self.characteristic = characteristics.characteristic(debug)
  self.DICT = self.util.getDICT()
  self.reset()

 def reset(self):
  self.first_approach = { }

 def do_analysis(self, data):
  # 1) pre-scan to know where a word starts/ends and  how many words we got
  #    we try to find words based on the meta data but also try to find the
  #    start based on a rough first token analysis

  # l = sorted(l, key=lambda x: -x[1])

  tokenized, words_start_guess = self.pre_scan(data)
 
  # 2) based on the best guess tokenizer list we will now
  #    compare the tokens against our dictionary entries

  words = self.word_scan(words_start_guess, data)

  matches = self.fast_scan(tokenized, words, data)

  if (matches != None):
   sorted_matches = sorted(matches, key=lambda x: -x[1])
   print sorted_matches

 def word_scan(self, words_start_guess, data):
  words = { }
  for a in words_start_guess:
   if (a[2] not in words):
    words[a[2]] = [ a[0], a[1] ]
   elif (a[0] > words[a[2]][0]):
    words[a[2]][0] = a[0]
    words[a[2]][1] = a[1]
  return words

 def fast_scan(self, tokenized, words, data):
  matches = [ ]
  if (len(tokenized) == 0):
   return None # TODO: Check for words and/or run complete analysis against data!!!
  else:
   ti = 0
   for s in range(0, len(tokenized)):
    if (s+1 == len(tokenized) and tokenized[s] < len(data)):
     self.fast_token_iter(tokenized[s], len(data), data, matches)
    else:
     self.fast_token_iter(tokenized[s], tokenized[s+1], data, matches)
    ti += 1
   self.full_compare(words, data, matches)
  return matches 

 def fast_token_iter(self, s, e, data, matches):
  for dict_entries in self.DICT['dict']:
   pos = 0
   word_match = 0
   wdl = 0
   id = dict_entries['id']
   for i in range(s,e):
    o = data[i]
    c,m = o
    if (c != None):
     result = self.fast_token_compare(c, id, pos)
     match, dl = result
     word_match += match
     wdl = dl
     pos += 1
    else:
     break
   word_match = word_match / wdl
   matches.append([s, word_match, id])

 def full_compare(self, words, data, matches):
  for id in words:
   s = words[id][1]
   pos = 0
   wdl = 0
   word_match = 0
   for i in range(s, len(data)):
    o = data[i]
    c,m = o
    if (c != None):
     result = self.fast_token_compare(c, id, pos)
     match, dl = result
     word_match += match
     wdl = dl
     pos += 1
    else:
     break
   word_match = word_match / wdl
   matches.append([s, word_match, id])

 def fast_token_compare(self, characteristic, id, pos):
  match = 0
  for dict_entries in self.DICT['dict']:
   if (dict_entries['id'] == id):
    dict_characteristic = dict_entries['characteristic']
    characteristic_tokens = dict_characteristic['tokens']
    if (len(characteristic_tokens) > pos):
     token = characteristic_tokens[pos]
     min_approach = self.characteristic.get_approach(token['fft_avg_min'])
     max_approach = self.characteristic.get_approach(token['fft_avg_max'])
     match = self.compare_fft_token_approach(characteristic['fft_approach'], min_approach, max_approach)
     match += self.compare_token(characteristic['fft_avg'], token['fft_avg_min'], token['fft_avg_max'])
     match += self.compare_tendency(characteristic, token)
     return match, len(characteristic_tokens)
    else:
     return 0, len(characteristic_tokens)

 def pre_scan(self, data):
  tokenized = [ ]
  words_start_guess = [ ]
  lh = -1
  for i, o in enumerate(data):
   c, m = o
   if (c != None and 'word_length' in m[0]):
    if (lh > m[0]['word_length'] or lh == -1):
     tokenized.append(i)
    lh = m[0]['word_length']
    words_start_guess.extend(self.guess_word_start(c, i))
  return tokenized, words_start_guess

 def guess_word_start(self, characteristic, pos):
  best_guesses = [ ]
  for dict_entries in self.DICT['dict']:
   dict_characteristic = dict_entries['characteristic']
   characteristic_tokens = dict_characteristic['tokens']
   token = characteristic_tokens[0]
   # we only compare the first token as we want to find the beginng of a known word!
   min_approach = self.characteristic.get_approach(token['fft_avg_min'])
   max_approach = self.characteristic.get_approach(token['fft_avg_max'])
   guess = self.compare_fft_token_approach(characteristic['fft_approach'], min_approach, max_approach)
   guess += self.compare_tendency(characteristic, token)
   best_guesses.append([guess, pos, dict_entries['id']])
  return best_guesses

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
    if (i < len(globalvars.IMPORTANCE)):
     factor = globalvars.IMPORTANCE[i]
    match += factor
  guessing = int(match*100/len(zipped))
  return guessing

 def compare_fft_token_approach(self, cfft, mifft, mafft):
  zipped = zip(cfft, mifft, mafft)
  perfect_match = 0
  approach_match = 0
  lz = len(zipped)
  cut = lz / 3
  if (cut < 10): cut = 20
  consider = 0
  for i,z in enumerate(zipped):
   a, b, c = z
   if (a < cut):
    if (a >= b and a <= c):
     factor = 1
     if (a < len(globalvars.IMPORTANCE)):
      factor = globalvars.IMPORTANCE[a]
     perfect_match += factor
    else:
     approach_match += self.find_approach_match(i, b, c, cfft)
    consider += 1
  guess = int(perfect_match + approach_match * 100 / consider)
  return guess

 def find_approach_match(self, i, b, c, cfft):
  index = [ ]
  match = 0
  if (b in cfft):
   index.append(cfft.index(b))
  if (c in cfft):
   index.append(cfft.index(c))
  for a in index:
   factor = 1
   if (a < len(globalvars.IMPORTANCE)):
    factor = globalvars.IMPORTANCE[a]
   if (a >= 0 and i >= a-factor and i <= a+factor):
    if (i > a):
     factor = i - a
    else:
     factor = a - i
   match += factor 
  if (match > 0):
   match = match / 2
  return match
