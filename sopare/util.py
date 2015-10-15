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

import json
import wave
import uuid
from path import __wavedestination__

class util:

 # min. sequence of silence for trim
 TRIM_SILENCE = 1000
 # min value to detect a silence period
 MIN_SILENCE_COUNTER = 10
 # value to detect words and not syllables
 MIN_WORD_LENGTH_DETECTOR = 20

 def __init__(self, debug, wave):
  self.debug = debug
  self.wave = wave

 def trim(self, tendency_model):
  COMPUTE_SILENCE = (sum(tendency_model) / len(tendency_model) * 2)
  for p in range (len(tendency_model)-1, 0, -1):
   if (tendency_model[p] > COMPUTE_SILENCE):
    if (p+4 < len(tendency_model)):
     p += 4
    return tendency_model[0:p]
  return tendency_model

 def ltrim(self, data):
  silence = 0
  for p in range(0, len(data)-1):
   if (data[p] < self.TRIM_SILENCE):
    silence += 1
    if (silence == self.MIN_SILENCE_COUNTER):
     return data[0:p]
   else:
    silence = 0
  return data  

 def tokenizer(self, data, rawdata):
  tokens = [ ]
  positions = [ ]
  final_positions = [ ]
  avg = 0
  for n in data:
   avg += n
  avg = avg / len(data)
  if (self.debug):
   print ("avg = "+str(avg))
  pos = 0
  seeker = False
  freq_count = 0
  laststart = 0
  silence_avg = 0
  silence_counter = 0
  for n in data:
   if (n >= avg):
    if (seeker == True):
     seeker = False
     if (silence_counter > self.MIN_SILENCE_COUNTER):
      if (self.debug):
       print ("silence found at "+str(laststart))
      positions.append(laststart)
       
    silence_counter = 0
    silence_avg = 0
    freq_count += 1
    if (freq_count > self.MIN_WORD_LENGTH_DETECTOR):
     seeker = True
    else:
     seeker = False
   if (n < avg and seeker == True):
    # we need to find a short period of "silence"
    laststart = pos
    silence_counter += 1
    silence_avg += n
   pos += 1


  last = 0
  token = 0
  for p in positions:
   diff = p - last
   if (diff >= self.MIN_WORD_LENGTH_DETECTOR):
    final_positions.append(p)
   elif (token > 1):
    final_positions[len(final_positions)-1] = p
   token += 1 
   last = p

  last = 0
  token = 0
  if (len(final_positions) > 0):
   for p in final_positions:
    tokens.append(data[last:p])
    if (self.wave):
     self.savewave(last, p, token, rawdata)
    token += 1
    last = p
   if (last <= len(data)):
    tokens.append(data[last:])
    if (self.wave):
     self.savewave(last, len(data), token, rawdata)
  else:
   tokens.append(data)

  if (self.debug):
   print ("tokens before trim "+str(tokens))

  final_tokens = [ ]
  for token in tokens:
   final_tokens.append(self.ltrim(token))

  if (self.debug):
   print ("final tokens "+str(final_tokens))
  return final_tokens

 def get_characteristic_by_name_from_dict(self, dict, JSON_DICT):
  dict_objects = JSON_DICT['dict']
  for do in dict_objects:
   if (dict == do['id']):
    c = do['characteristic']
    return c
  return None

 def add2dict(self, obj, dict):
  json_obj = self.getDICT()
  json_obj['dict'].append({'id': dict, 'characteristic': obj, 'uuid': str(uuid.uuid4())})
  self.writeDICT(json_obj)
  return json_obj

 def writeDICT(self, json_data):
  with open("dict/dict.json", 'w') as json_file:
   json.dump(json_data, json_file)
  json_file.close()

 def getDICT(self):
  with open("dict/dict.json") as json_file:
   json_data = json.load(json_file)
  json_file.close()
  return json_data

 def deletefromdict(self, dict):
  json_obj = self.getDICT()
  new_dict = { 'dict': [ ] }
  if (dict != '*'):
   dict_objects = json_obj['dict']
   for do in dict_objects:
    if (do['id'] != dict):
     new_dict['dict'].append(do)
  self.writeDICT(new_dict)

 def deleteuuidfromdict(self, uuid):
  json_obj = self.getDICT()
  new_dict = { 'dict': [ ] }
  dict_objects = json_obj['dict']
  for do in dict_objects:
   if (do['uuid'] != uuid):
    new_dict['dict'].append(do)
  self.writeDICT(new_dict)

 def saverawwave(self, filename, start, end, raw):
  wf = wave.open(__wavedestination__+filename+".wav", 'wb')
  wf.setnchannels(1)
  wf.setsampwidth(2)
  wf.setframerate(44100)
  data = raw[start:end] 
  wf.writeframes(b''.join(data))

 def normalize(self, data, normalize):
  newdata = [(float(i)/sum(data)*normalize) for i in data]
  return newdata
