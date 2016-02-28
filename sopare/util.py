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
import config
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
            print (dict_entries['id'] + ' ' + dict_entries['uuid'])

    def showdictentry(self, id):
        json_data = self.getDICT()
        for dict_entries in json_data['dict']:
           if dict_entries['id'] == id:
               print (dict_entries['uuid'])
               print (dict_entries['word_tendency'])
               for characteristic in dict_entries['characteristic']:
                   print (characteristic['tendency'])
               for characteristic in dict_entries['characteristic']:
                   print (characteristic['fft_approach'])
               for characteristic in dict_entries['characteristic']:
                   print (characteristic['fft_max'])


    def compile_analysis(self):
        analysis = { }
        json_data = self.getDICT()
        for dict_entries in json_data['dict']:
            if (dict_entries['id'] not in analysis):
                analysis[dict_entries['id']] = { 'min_tokens': 0, 'max_tokens': 0, 'min_max': 0, 'max_max': 0, 'min_peaks': 0, 'max_peaks': 0, 'min_fft_len': 0, 'max_fft_len': 0, 'min_delta': 0, 'max_delta': 0, 'min_length': 0, 'max_length': 0, 'min_fft_avg': [ ] , 'max_fft_avg': [ ] }
            l = len(dict_entries['characteristic'])
            if (l > analysis[dict_entries['id']]['max_tokens']):
                analysis[dict_entries['id']]['max_tokens'] = l
            if (l < analysis[dict_entries['id']]['min_tokens'] or analysis[dict_entries['id']]['min_tokens'] == 0):
                analysis[dict_entries['id']]['min_tokens'] = l
            if (dict_entries['word_tendency']['max'] < analysis[dict_entries['id']]['min_max'] or analysis[dict_entries['id']]['min_max'] == 0):
                analysis[dict_entries['id']]['min_max'] = dict_entries['word_tendency']['max']
            if (dict_entries['word_tendency']['max'] > analysis[dict_entries['id']]['max_max']):
                 analysis[dict_entries['id']]['max_max'] = dict_entries['word_tendency']['max']
            if (dict_entries['word_tendency']['peaks'] < analysis[dict_entries['id']]['min_peaks'] or analysis[dict_entries['id']]['min_peaks'] == 0):
                analysis[dict_entries['id']]['min_peaks'] = dict_entries['word_tendency']['peaks']
            if (dict_entries['word_tendency']['peaks'] > analysis[dict_entries['id']]['max_peaks']):
                 analysis[dict_entries['id']]['max_peaks'] = dict_entries['word_tendency']['peaks']
            for i, characteristic in enumerate(dict_entries['characteristic']):
                if (len(analysis[dict_entries['id']]['min_fft_avg']) <= i):
                 fft_avg_min = [0] * len(config.IMPORTANCE)
                 fft_avg_max = [0] * len(config.IMPORTANCE)
                 analysis[dict_entries['id']]['min_fft_avg'].append(fft_avg_min)
                 analysis[dict_entries['id']]['max_fft_avg'].append(fft_avg_max)
                fft_len = characteristic['fft_freq']
                length = characteristic['tendency']['len']
                delta = characteristic['tendency']['delta']
                fft_avg = characteristic['fft_avg']
                if (fft_len > analysis[dict_entries['id']]['max_fft_len']):
                    analysis[dict_entries['id']]['max_fft_len'] = fft_len
                if (fft_len < analysis[dict_entries['id']]['min_fft_len'] or analysis[dict_entries['id']]['min_fft_len'] == 0):
                    analysis[dict_entries['id']]['min_fft_len'] = fft_len
                if (delta > analysis[dict_entries['id']]['max_delta']):
                    analysis[dict_entries['id']]['max_delta'] = delta
                if (delta < analysis[dict_entries['id']]['min_delta'] or analysis[dict_entries['id']]['min_delta'] == 0):
                    analysis[dict_entries['id']]['min_delta'] = delta
                if (length > analysis[dict_entries['id']]['max_length']):
                    analysis[dict_entries['id']]['max_length'] = length
                if (length < analysis[dict_entries['id']]['min_length'] or analysis[dict_entries['id']]['min_length'] == 0):
                    analysis[dict_entries['id']]['min_length'] = length
                for j, fft in enumerate(fft_avg):
                    if (j < len(config.IMPORTANCE)):
                        if (fft > analysis[dict_entries['id']]['max_fft_avg'][i][j]):
                             analysis[dict_entries['id']]['max_fft_avg'][i][j] = fft
                        if (fft < analysis[dict_entries['id']]['min_fft_avg'][i][j] or  analysis[dict_entries['id']]['min_fft_avg'][i][j] == 0):
                             analysis[dict_entries['id']]['min_fft_avg'][i][j] = fft
        return analysis

    def learndict(self, characteristics, word_tendency, id):
        json_data =  self.getDICT()
        dict_model = self.prepare_dict_model(characteristics)
        self.add2dict(dict_model, word_tendency, id)

    def prepare_dict_model(self, characteristics):
        tokens = [ ]
        for o in characteristics:
            characteristic, meta = o
            for m in meta:
                token = m['token']            
                if (token != 'stop'):
                    if (characteristic != None):
                        tokens.append(characteristic)
                    if (token == 'word' or token == 'long silence'):
                        break
        return tokens

    def add2dict(self, obj, word_tendency, id):
        json_obj = self.getDICT()
        json_obj['dict'].append({'id': id, 'characteristic': obj, 'word_tendency': word_tendency, 'uuid': str(uuid.uuid4())})
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

    def deletefromdict(self, id):
        json_obj = self.getDICT()
        new_dict = { 'dict': [ ] }
        if (id != '*'):
            dict_objects = json_obj['dict']
            for do in dict_objects:
                if (do['id'] != id):
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
