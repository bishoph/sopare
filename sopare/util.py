#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015, 2016 Martin Kauss (yo@bishoph.org)

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

import characteristics
import json
import wave
import uuid
import numpy
import globalvars
from scipy.io.wavfile import write
from path import __wavedestination__

class util:

    def __init__(self, debug, wave):
        self.debug = debug
        self.wave = wave
        self.characteristic = characteristics.characteristic(debug)

    def showdictentriesbyid(self):
        json_data = self.getDICT()
        for dict_entries in json_data['dict']:
            print dict_entries['id']

    def showdictentry(self, dict):
        json_data = self.getDICT()
        dict_entries = self.get_characteristic_by_name_from_dict(dict, json_data)
        if (dict_entries != None):
            dict_characteristic = dict_entries['characteristic']
            characteristic_tokens = dict_characteristic['tokens']
            for i, token in enumerate(characteristic_tokens):
                maxv = str(token['fft_avg_max'])
                minv = str(token['fft_avg_min'])
                maxv = maxv[1:len(maxv)-1]
                minv = minv[1:len(minv)-1]    
                print ('max-avg ['+str(i)+'] '+dict+', '+maxv)
                print ('min-avg ['+str(i)+'] '+dict+', '+minv)
            for i, token in enumerate(characteristic_tokens):
                print ('min-/max freq ['+str(i)+'] '+dict+', '+str(token['fft_freq_max'])+' '+str(token['fft_freq_min']))
            for i, token in enumerate(characteristic_tokens):
                 for z, approach in enumerate(token['fft_approach']):
                    sa = str(approach)
                    sa = sa[1:len(sa)-1]
                    print ('approach ['+str(i)+'-'+str(z)+'], '+str(sa))
            for i, token in enumerate(characteristic_tokens):
                tendency = token['tendency']
                print ('['+str(i)+'] = '+str(tendency))
        else:
            print ('No dict entry available!') 

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
                break
        if (token == None):
            if (self.debug):
                print ('Creating new zone model due to new num '+str(num))
            zone_model = self.create_zone_model(num, characteristic)
            dict_model['characteristic']['tokens'].append(zone_model)
        else:
            if (self.debug):
                print ('Enhancing existing zone model num = '+str(num))
            self.modify_zone_model(characteristic, token)
        return dict_model

    def modify_zone_model(self, characteristic, token):
        self.zoning('fft_avg', 'fft_avg_min', characteristic, token, 0)
        self.zoning('fft_avg', 'fft_avg_max', characteristic, token, 1)
        token['fft_approach'].append(characteristic['fft_approach'])
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
        if (characteristic['tendency']['len'] > token['tendency']['len_max']):
            token['tendency']['len_max'] = characteristic['tendency']['len']
        if (characteristic['tendency']['avg'] < token['tendency']['avg_min']):
            token['tendency']['avg_min'] = characteristic['tendency']['avg']
        if (characteristic['tendency']['avg'] > token['tendency']['avg_max']):
            token['tendency']['avg_max'] = characteristic['tendency']['avg'] 
        if (characteristic['tendency']['delta'] < token['tendency']['delta_min']):
            token['tendency']['delta_min'] = characteristic['tendency']['delta']
        if (characteristic['tendency']['delta'] > token['tendency']['delta_max']):
            token['tendency']['delta_max'] = characteristic['tendency']['delta']

    def zoning(self, id1, id2, characteristic, token, action):
        # We want a high precision even in our model and this means
        # too big steps are counter productive and we make sure that
        # our steps are somehow smooth.
        # Higher values means faster learning but also potential inaccuracy
        # and false positives!
   
        max_steps = 500

        obj = zip(characteristic[id1], token[id2])
        for i, o in enumerate(obj):
            co, to = o
            if (action == 0 and co < to):
                if (to-co > max_steps):
                    factor = .1
                    if (i < len(globalvars.ACCURACY)):
                        factor = globalvars.ACCURACY[i]
                    co = int(to - (max_steps*factor))
                    token[id2][i] = co
            elif (action == 1 and co > to):
                if (co-to > max_steps):
                    factor = .1
                if (i < len(globalvars.ACCURACY)):
                    factor = globalvars.ACCURACY[i]
                co = int(to + (max_steps * factor))
                token[id2][i] = co

    def create_zone_model(self, num, characteristic):
        characteristic_tendency = { 'peaks_min': characteristic['tendency']['peaks'] , 'peaks_max': characteristic['tendency']['peaks'], 'len_min': characteristic['tendency']['len'], 'len_max': characteristic['tendency']['len'], 'avg_min': characteristic['tendency']['avg'], 'avg_max': characteristic['tendency']['avg'], 'delta_min': characteristic['tendency']['delta'], 'delta_max': characteristic['tendency']['delta'] } 
        dict_model = { 'num': num, 'fft_approach': [ characteristic['fft_approach'] ] , 'fft_freq_min': characteristic['fft_freq'], 'fft_freq_max': characteristic['fft_freq'], 'fft_avg_max': characteristic['fft_avg'], 'fft_avg_min': characteristic['fft_avg'], 'tendency': characteristic_tendency }
        return dict_model 

    def get_characteristic_by_name_from_dict(self, dict, JSON_DATA):
        dict_entries = JSON_DATA['dict']
        for de in dict_entries:
            if (dict == de['id']):
                return de
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
            json.dump(json_data, json_file, indent=1, separators=(',', ': '))
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
        wf = wave.open(__wavedestination__+filename+'.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        data = raw[start:end] 
        wf.writeframes(b''.join(data))

    def savefilteredwave(self, filename, buffer):
        scaled = numpy.int16(buffer/numpy.max(numpy.abs(buffer)) * 32767)
        write(__wavedestination__+filename+'.wav', 44100, scaled)  

    def normalize(self, data, normalization):
        newdata = [int(float(i)/sum(data)*normalization) for i in data]
        return newdata
