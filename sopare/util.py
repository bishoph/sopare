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

 def __init__(self, debug, wave):
  self.debug = debug
  self.wave = wave

 def learndict(self, num, characteristic, dict):
  json_data =  self.getDICT()
  dict_model = self.get_characteristic_by_name_from_dict(dict, json_data)
  if (dict_model == None):
   dict_model = { 'tokens': [ self.create_zone_model(num, characteristic) ] }
   self.add2dict(dict_model, dict)
  else:
   dict_model = self.enhance_zone_model(num, characteristic, dict_model)
   self.changedict(dict_model, dict)

 def enhance_zone_model(self, num, characteristic, dict_model):
  tokens = dict_model['characteristic']['tokens']
  token = None
  for t in tokens:
   if ('num' in t and t['num'] == num):
    token = t   
  if (token == None):
   if (self.debug):
    print ('Creating new zone model due to new num '+str(num))
   zone_model = self.create_zone_model(num, characteristic)
   dict_model['characteristic']['tokens'].append(zone_model)
  else:
   if (self.debug):
    print ('Enhancing existing zone model num = '+str(num))
   self.modify_zone_model(num, characteristic, token)
  return dict_model

 def modify_zone_model(self, num, characteristic, token):
  self.zoning('fft_min', 'fft_min_min', characteristic, token, 0)
  self.zoning('fft_max', 'fft_max_min', characteristic, token, 0)
  self.zoning('fft_min', 'fft_min_max', characteristic, token, 1)
  self.zoning('fft_max', 'fft_max_max', characteristic, token, 1)
  if (characteristic['fft_freq'] < token['fft_freq_min']):
   token['fft_freq_min'] = characteristic['fft_freq']
  if (characteristic['fft_freq'] > token['fft_freq_max']):
   token['fft_freq_max'] = characteristic['fft_freq']
  if (characteristic['tendency']['peaks'] < token['tendency']['peaks_min']):
   token['peaks_min'] = characteristic['tendency']['peaks']
  if (characteristic['tendency']['peaks']  > token['tendency']['peaks_max']):
   token['peaks_max'] = characteristic['tendency']['peaks']
  if (characteristic['tendency']['len'] < token['tendency']['len_min']):
   token['tendency']['len_min'] = characteristic['tendency']['len']
  if (characteristic['tendency']['len'] < token['tendency']['len_max']):
   token['tendency']['len_max'] = characteristic['tendency']['len']
   

 def zoning(self, id1, id2, characteristic, token, action):
  obj = zip(characteristic[id1], token[id2])
  for i, o in enumerate(obj):
   co, to = o
   if (action == 0 and co < to):
    token[id2][i] = co
   elif (action == 1 and co > to):
    token[id2][i] = co

 def create_zone_model(self, num, characteristic):
  characteristic_tendency = { 'peaks_min': characteristic['tendency']['peaks'] , 'peaks_max': characteristic['tendency']['peaks'], 'len_min': characteristic['tendency']['len'], 'len_max': characteristic['tendency']['len'] } 
  dict_model = { 'num': num, 'fft_freq_min': characteristic['fft_freq'], 'fft_freq_max': characteristic['fft_freq'], 'fft_max_max': characteristic['fft_max'], 'fft_max_min': characteristic['fft_max'], 'fft_min_max': characteristic['fft_min'], 'fft_min_min': characteristic['fft_min'], 'tendency': characteristic_tendency } 
  return dict_model 

 def get_characteristic_by_name_from_dict(self, dict, JSON_DATA):
  dict_objects = JSON_DATA['dict']
  for do in dict_objects:
   if (dict == do['id']):
    return do
  return None

 def changedict(self, obj, dict):
  json_obj = self.getDICT()
  new_dict = { 'dict': [ ] }
  dict_objects = json_obj['dict']
  for do in dict_objects:
   if (do['id'] != dict):
    new_dict['dict'].append(do)
   else:
    new_dict['dict'].append(obj)
  self.writeDICT(new_dict)
  return new_dict

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
