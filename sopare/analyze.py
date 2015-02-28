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

import visual
import util
import characteristics

class approach:

 # throw away characteristics with a value below NOISE_TRESHOLD
 NOISE_TRESHOLD = 1000
 
 # only add matches that score at least MIN_MATCHES_TO_CONSIDER to results
 MIN_MATCHES_TO_CONSIDER = 2

 def __init__(self, debug, plot, dict):
  self.debug = debug
  self.plot = plot
  self.dict = dict
  self.util = util.util(debug)
  self.JSON_DICT = self.util.getDICT()
  self.character = characteristics.characteristic(self.debug)

 def analyze(self, data, rawdata):

  if (len(data) == 0):
   return

  rough = [ ]
  for obj in data:
   if (len(obj) == 1 and obj[0] == -999):
    pass
   else:
    for c in obj:
     rough.append(c)

  tendency_model = self.model_tendency(rough) 

  if (self.debug):
   print ("###########################################")
   print ("tendency model orig = " + str(tendency_model))

  # cut silence from end
  tendency_model = self.util.trim(tendency_model)
  if (self.debug):
   print ("tendency model trim = " + str(tendency_model))
   
  if (self.plot):
   x = visual.visual()
   x.create_sample(tendency_model, 'tendency.png')

  tokens = self.util.tokenizer(tendency_model, rawdata)
 
  dict_entry = None
  learn = False
  if (self.dict != None):
   print ("getting dict from dict")
   dict_entry = self.util.get_characteristic_by_name_from_dict(self.dict, self.JSON_DICT)
   learn = True
 
  count = 0
  results = [ ]
  for token in tokens: 
   characteristic = self.character.getcharacteristic(token, dict_entry, learn)

   if (self.dict != None and count == 0):
    # we only add the first word to the dict
    print ("adding characteristic ("+str(characteristic)+") for "+self.dict+ " to dictionary")
    self.JSON_DICT = self.util.add2dict(characteristic, self.dict, learn)

   if (self.debug):
    print ("characteristic = "+str(characteristic))

   results.append(self.compare(characteristic, count))
   count += 1

  if (len(results) > 0):
   for result in results:
    if (len(result) > 0):
     print ("Match = "+str(result))

 def compare(self, current_characteristic, count):
  results = [ ]
  dict_objects = self.JSON_DICT['dict']
  for dict_entry in dict_objects:
   id = dict_entry['id']
   dict_characteristic = dict_entry['characteristic']
   if (self.debug):
    print ("comparing "+id+" with characteristic")

   bestmatch = 0

   min_length = 0
   max_length = 0
   min_peaks = 0
   max_peaks = 0
   min_topstart = 0
   max_topstart = 0
   min_topend = 0
   max_topend = 0

   max = 0
   length = 0
   peaks = 0
   base = 0 
   topstart = 0
   topend = 0

   for elements in dict_characteristic:
    if ('min_length' in elements):
     min_length = elements['min_length']
    if ('max_length' in elements):
     max_length = elements['max_length']
    if ('min_peaks' in elements):
     min_peaks = elements['min_peaks']
    if ('max_peaks' in elements):
     max_peaks = elements['max_peaks']
    if ('min_topstart' in elements):
     min_topstart = elements['min_topstart']
    if ('max_topstart' in elements):
     max_topstart = elements['max_topstart']
    if ('min_topend' in elements):
     min_topend = elements['min_topend']
    if ('max_topend' in elements):
     max_topend = elements['max_topend']

   for elements in current_characteristic:
    if ('length' in elements):
     length = elements['length']
    if ('topstart' in elements):
     topstart = elements['topstart']
    if ('topend' in elements):
     topend = elements['topend']
    if ('base' in elements):
     base = elements['base']
    if ('peaks' in elements):
     peaks = elements['peaks']
    if ('max' in elements):
     max = elements['max']   

   match_statistics = ""
   score = 0
   counter = 0
   # check the base and the max value to see if this is just noise!
   if (max < self.NOISE_TRESHOLD):
    return results

   if (peaks >= min_peaks and peaks <= max_peaks):
    score += 40
    counter += 1
    match_statistics += "p"
   if (topstart >= min_topstart and topstart <= max_topstart):
    score += 10
    counter += 1
    match_statistics += "s"
   if (topend >= min_topend and topend <= max_topend):
    score += 10
    counter += 1
    match_statistics += "e"
   if (length >= min_length and peaks <= max_length):
    score += 40
    counter += 1
    match_statistics += "l"
   if (counter > 0):
    score = score * counter / 4
  
   if (self.debug):
    print ("we got score "+str(score) + " for "+id)  

   if (score > bestmatch and counter >= self.MIN_MATCHES_TO_CONSIDER):
    results.append([count, id, score, match_statistics])
    bestmatch = score

  return results

    
 def model_tendency(self, data):
  if (self.plot):
   x = visual.visual()
   x.create_sample(data, 'compressed.png')
  last = 0
  last_high = 0
  tendency = [ ]
  counter = 0
  for n in data:
   if (n < 0):
    n = 0 - n
   if (n >= 0 and n > last_high):
     last_high = n
   if (counter == 8):
    if (last < last_high):     
     tendency.append(int(last))
    elif (last > last_high):
     tendency.append(int(last))
    last = last_high
    last_high = 0
    counter = 0
   else:
    counter += 1
  return tendency  
   

