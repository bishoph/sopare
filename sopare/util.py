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
import math
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

    def showdictentry(self, sid):
        json_data = self.getDICT()
        ids = [ ]
        for dict_entries in json_data['dict']:
           if ((dict_entries['id'] == sid or sid == "*") and dict_entries['id'] not in ids):
               ids.append(dict_entries['id'])
        l_arr = { }
        for id in ids:
            for dict_entries in json_data['dict']:
                if (id == dict_entries['id']):
                    if (id not in l_arr):
                        l_arr[id] = { 'length': [ ] }
                    ll = len(dict_entries['characteristic'])
                    if (ll not in l_arr[id]['length']):
                        l_arr[id]['length'].append(ll)
        for id in l_arr:
            ml = max(l_arr[id]['length'])
            for i in range(0, ml):
                for dict_entries in json_data['dict']:
                    if (dict_entries['id'] == id  and len(dict_entries['characteristic']) > i):
                        output = str(dict_entries['characteristic'][i]['fft_max'])
                        print (id + '-' + str(i)+  ', '+ output[1:len(output)-1] )

    def compile_analysis(self, json_data):
        analysis = { }
        for dict_entries in json_data['dict']:
            if ('word_tendency' in dict_entries and dict_entries['word_tendency'] != None):
                if (dict_entries['id'] not in analysis):
                    analysis[dict_entries['id']] = { 'min_tokens': 0, 'max_tokens': 0, 'min_peaks': 0, 'max_peaks': 0, 'min_peak_length': [ ], 'max_peak_length': [ ], 'min_fft_len': 0, 'max_fft_len': 0, 'min_delta': 0, 'max_delta': 0, 'min_length': 0, 'max_length': 0, 'first_token': [ ], 'shape': [ ] }
                l = len(dict_entries['characteristic'])
                if (l < 2):
                    print ('the following characteristic is < 2!')
                    print dict_entries['id'], l, dict_entries['uuid']
                if (l > analysis[dict_entries['id']]['max_tokens']):
                    analysis[dict_entries['id']]['max_tokens'] = l
                l = l - 1 # TODO: Check if this is really necessary
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
                    if (characteristic['weighting'] > .9):
                        analysis[dict_entries['id']]['first_token'].append((characteristic['tendency'], characteristic['fft_outline'], characteristic['fft_max']))
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
                        self.add_weighting(tokens)
                        compiled_dict['dict'].append({'id': json_obj['id'], 'characteristic': tokens, 'word_tendency': json_obj['word_tendency'], 'uuid': file_uuid })
                    else:
                        print (json_obj['id'] + ' ' + file_uuid+ ' got no tokens!')
                raw_json_file.close()
        return compiled_dict

    def add_weighting(self, tokens):
        weighting = 0
        w_arr = [ ]
        for token in tokens:
            c_weighting = token['tendency']['avg'] * token['tendency']['len']
            if (c_weighting > weighting):
                weighting = c_weighting
            w_arr.append(c_weighting)
        high = max(w_arr)
        for i, weighting in enumerate(w_arr):
            v = (1.0 - (i*0.1)) # TODO: Add magic
            tokens[i]['weighting'] = v

    def compress_dict(self, json_data):
        compressed_dict =  { 'dict': [ ] }
        for dict_entries in json_data['dict']:
            self.check_compression(dict_entries, compressed_dict)
        print ('compression: ' + str(len(json_data['dict'])) + ' / ' + str(len(compressed_dict['dict'])))
        return compressed_dict

    def check_compression(self, dict_entries, compressed_dict):
        id = dict_entries['id']
        ll = len(dict_entries['characteristic'])
        if (len(compressed_dict['dict']) == 0):
            compressed_dict['dict'].append({'id': id, 'characteristic': dict_entries['characteristic'], 'word_tendency': { }, 'uuid': 'x-'+id+'-'+str(ll) })
        else:
            contains = False
            for compressed_dict_entries in compressed_dict['dict']:
                if (id == compressed_dict_entries['id'] and ll == len(compressed_dict_entries['characteristic'])):
                    contains = True
                    for i, characteristic in enumerate(dict_entries['characteristic']):
                        tendency = characteristic['tendency']
                        fft_freq = characteristic['fft_freq']
                        dict_tendency = compressed_dict_entries['characteristic'][i]['tendency']
                        dict_fft_freq = compressed_dict_entries['characteristic'][i]['fft_freq']
                        tendency_similarity = self.approach_similarity(
                         [fft_freq, tendency['len'], tendency['avg'], tendency['delta'], tendency['deg']],
                         [dict_fft_freq, dict_tendency['len'], dict_tendency['avg'], dict_tendency['delta'], dict_tendency['deg']]
                        )
                        
                        fft_max = characteristic['fft_max']
                        dict_fft_max = compressed_dict_entries['characteristic'][i]['fft_max']
                        fft_similarity = self.approach_similarity(fft_max, dict_fft_max)
                        if (config.USE_LENGTH_SIMILARITY):
                            fft_length_similarity = self.approach_length_similarity(fft_max, dict_fft_max)
                            fft_similarity = fft_similarity * fft_length_similarity
                        if (tendency_similarity < config.MIN_READABLE_RESULT_VALUE or fft_similarity < config.MIN_READABLE_RESULT_VALUE):
                            contains = False
            if (contains == False):
                compressed_dict['dict'].append({'id': id, 'characteristic': dict_entries['characteristic'], 'word_tendency': { }, 'uuid': 'x-'+id+'-'+str(ll) })
            else:
                if (self.debug):
                    print ('Not considering ' + dict_entries['uuid'] + ' (' + id + ') from dict because we have a similar object already.')
           

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

    def approach_distance(self, arr1, arr2):
        return math.sqrt(sum(pow(a - b, 2) for a, b in zip(arr1, arr2)))

    def sqr(self, arr):
        return round(math.sqrt(sum([a * a for a in arr])), 2)

    def approach_similarity(self, arr1, arr2):
        n = sum(a * b for a, b in zip(arr1, arr2))
        d = self.sqr(arr1) * self.sqr(arr2)
        return round(n / float(d), 2)

    def approach_length_similarity(self, arr1, arr2):
        larr1 = sum(arr1)
        larr2 = sum(arr2)
        return min(larr1, larr2) / float(max(larr1, larr2))

    def approach_intersection(self, arr1, arr2):
       return list(set(arr1).intersection(arr2))
