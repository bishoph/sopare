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
import config
import numpyjsonencoder
import json
import wave
import uuid
import numpy
import os
import heapq
import datetime
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
           if dict_entries['id'] == id or id == "*":
               print (dict_entries['uuid'])
               print (dict_entries['word_tendency'])
               for characteristic in dict_entries['characteristic']:
                   print (characteristic['tendency'])
               for characteristic in dict_entries['characteristic']:
                   print (characteristic['fft_approach'])
               for characteristic in dict_entries['characteristic']:
                   print (characteristic['fft_max'])

    def compile_analysis(self, json_data):
        analysis = { }
        for dict_entries in json_data['dict']:
            if ('word_tendency' in dict_entries and dict_entries['word_tendency'] != None):
                if (dict_entries['id'] not in analysis):
                    analysis[dict_entries['id']] = { 'min_tokens': 0, 'max_tokens': 0, 'min_peaks': 0, 'max_peaks': 0, 'min_peak_length': [ ], 'max_peak_length': [ ], 'min_fft_len': 0, 'max_fft_len': 0, 'min_delta': 0, 'max_delta': 0, 'min_length': 0, 'max_length': 0, 'high5': [ ], 'shape': [ ] }
                l = len(dict_entries['characteristic'])
                if (l > analysis[dict_entries['id']]['max_tokens']):
                    analysis[dict_entries['id']]['max_tokens'] = l
                l = l - 1 # this is necessary as words in a sentence lacks often the last token!
                if (l < analysis[dict_entries['id']]['min_tokens'] or analysis[dict_entries['id']]['min_tokens'] == 0):
                    analysis[dict_entries['id']]['min_tokens'] = l
                if (dict_entries['word_tendency']['peaks'] < analysis[dict_entries['id']]['min_peaks'] or analysis[dict_entries['id']]['min_peaks'] == 0):
                    analysis[dict_entries['id']]['min_peaks'] = dict_entries['word_tendency']['peaks']
                if (dict_entries['word_tendency']['peaks'] > analysis[dict_entries['id']]['max_peaks']):
                     analysis[dict_entries['id']]['max_peaks'] = dict_entries['word_tendency']['peaks']
                analysis[dict_entries['id']]['shape'].append(dict_entries['word_tendency']['shape'])
                for i, pl in enumerate(dict_entries['word_tendency']['peak_length']):
                    if (len(analysis[dict_entries['id']]['min_peak_length']) <= i):
                        analysis[dict_entries['id']]['min_peak_length'].append(0)
                    if (len(analysis[dict_entries['id']]['max_peak_length']) <= i):
                        analysis[dict_entries['id']]['max_peak_length'].append(0)
                    if (pl < analysis[dict_entries['id']]['min_peak_length'][i] or analysis[dict_entries['id']]['min_peak_length'][i] == 0):
                        analysis[dict_entries['id']]['min_peak_length'][i] = pl
                    if (pl > analysis[dict_entries['id']]['max_peak_length'][i]):
                       analysis[dict_entries['id']]['max_peak_length'][i] = pl
                for i, characteristic in enumerate(dict_entries['characteristic']):
                    fft_len = characteristic['fft_freq']
                    length = characteristic['tendency']['len']
                    delta = characteristic['tendency']['delta']
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
                    fft_max = characteristic['fft_max']
                    dhi, dh, do = self.characteristic.get_approach(fft_max, config.FAST_HIGH_COMPARISON)
                    analysis[dict_entries['id']]['high5'].append((dhi, dh))
        return analysis

    def store_raw_dict_entry(self, dict_id, raw_characteristics, word_tendency):
        json_obj = {'id': dict_id, 'characteristic': raw_characteristics, 'word_tendency': word_tendency, 'created': datetime.datetime.now().isoformat() }
        with open("dict/"+str(uuid.uuid4())+".raw", 'w') as json_file:
            json.dump(json_obj, json_file, cls=numpyjsonencoder.numpyjsonencoder)
        json_file.close()

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
                    if (token == 'start analysis'):
                        break
        return tokens

    def add2dict(self, obj, word_tendency, id):
        json_obj = self.getDICT()
        json_obj['dict'].append({'id': id, 'characteristic': obj, 'word_tendency': word_tendency, 'uuid': str(uuid.uuid4())})
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

    def getCompiledDict(self):
        compiled_dict = { 'dict': [ ] }
        for filename in os.listdir("dict/"):
            if (filename.endswith(".raw")):
                fu = filename.split('.')
                file_uuid = fu[0]
                tokens = [ ]
                with open("dict/"+filename) as raw_json_file:
                    json_obj = json.load(raw_json_file, object_hook=numpyjsonencoder.numpyjsonhook)
                    json_obj['id']
                    for raw_obj in json_obj['characteristic']:
                        meta = raw_obj['meta']
                        fft = raw_obj['fft']
                        raw_tendency = raw_obj['raw_tendency']
                        characteristic = self.characteristic.getcharacteristic(fft, raw_tendency)
                        if (characteristic != None):
                            for m in meta:
                                if (m['token'] != 'stop'):
                                    tokens.append(characteristic)
                    if (len(tokens) > 0):
                        compiled_dict['dict'].append({'id': json_obj['id'], 'characteristic': tokens, 'word_tendency': json_obj['word_tendency'], 'uuid': file_uuid })
                    else:
                        print (json_obj['id'] + ' ' + file_uuid+ ' got no tokens!')
                raw_json_file.close()
        return compiled_dict

    def compress_dict(self, json_data):
        compressed_dict =  { 'dict': [ ] }
        ids = [ ]
        counter = 0
        for dict_entries in json_data['dict']:
           if (dict_entries['id'] not in ids):
               ids.append(dict_entries['id'])
           counter += 1
        print ('compressing ' + str(counter) +' entries into ' + str(len(ids)))
        for id in ids:
            counter = 0
            compressed_tokens = [ ]
            compressed_word_tendency = { 'counter': 0 }
            for dict_entries in json_data['dict']:
                if (id == dict_entries['id']):
                    characteristic = dict_entries['characteristic']
                    self.compress_characteristic(characteristic, compressed_tokens)
            # avg
            for token in compressed_tokens:
                avg_c = token['tendency']['counter']
                if (avg_c > 0):
                    token['fft_freq'] = token['fft_freq'] / avg_c
                    for key in token['tendency']:
                        token['tendency'][key] = token['tendency'][key] / avg_c
                    for i, fm in enumerate(token['fft_max']):
                        if (token['fft_max_avg_c'][i] > 0):
                            token['fft_max'][i] = fm  / token['fft_max_avg_c'][i]                
                    for i, fa in enumerate(token['fft_approach']):
                        token['fft_approach'][i] = fa  / avg_c
                    for i, fo in enumerate(token['fft_outline']):
                        token['fft_outline'][i] = fo  / avg_c
                # remove temp stuff
                del token['tendency']['counter']
                del token['fft_max_avg_c']

            compressed_dict['dict'].append({'id': id, 'characteristic': compressed_tokens, 'word_tendency': compressed_word_tendency, 'uuid': 'x'+id })
        return compressed_dict

    def compress_characteristic(self, characteristic, compressed_tokens):
        for i, c in enumerate(characteristic):
            if (i >= len(compressed_tokens)):
                compressed_tokens.append({ 'tendency': { 'counter': 0 }, 'fft_max': [ ], 'fft_approach': [ ], 'fft_outline': [ ], 'fft_freq': 0, 'fft_max_avg_c': [ ] })
            else:
                compressed_tokens[i]['tendency']['counter'] += 1
            compressed_tokens[i]['fft_freq'] += c['fft_freq']
            tendency = c['tendency']

            for key in tendency:
                if (key not in compressed_tokens[i]['tendency']):
                    compressed_tokens[i]['tendency'][key] = tendency[key]
                else:
                    compressed_tokens[i]['tendency'][key] += tendency[key]

            for j, fm in enumerate(c['fft_max']):
                if (j >= len(compressed_tokens[i]['fft_max'])):
                    compressed_tokens[i]['fft_max'].append(fm)
                    compressed_tokens[i]['fft_max_avg_c'].append(0)
                else:
                    compressed_tokens[i]['fft_max'][j] += fm
                    if (fm > 0):
                        compressed_tokens[i]['fft_max_avg_c'][j] += 1

            for j, fa in enumerate(c['fft_approach']):
                if (j >= len(compressed_tokens[i]['fft_approach'])):
                    compressed_tokens[i]['fft_approach'].append(fa)
                else:
                    compressed_tokens[i]['fft_approach'][j] += fa

            for j, fa in enumerate(c['fft_outline']):
                if (j >= len(compressed_tokens[i]['fft_outline'])):
                    compressed_tokens[i]['fft_outline'].append(fa)
                else:
                    compressed_tokens[i]['fft_outline'][j] += fa

    def deletefromdict(self, id):
        json_obj = self.getDICT()
        new_dict = { 'dict': [ ] }
        if (id != '*'):
            dict_objects = json_obj['dict']
            for do in dict_objects:
                if (do['id'] != id):
                     new_dict['dict'].append(do)
        self.writeDICT(new_dict)

    def recreate_dict_from_raw_files(self):
        self.writeDICT(self.getCompiledDict())

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

    def partition(self, n):
        p = set()
        p.add((n, ))
        for a in range(1, n):
            for b in self.partition(n - a):
                p.add((a, ) + b)
        return p
