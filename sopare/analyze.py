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

import util
import globalvars
import path
import imp
import os

class analyze():

    def __init__(self, debug):
        self.debug = debug
        self.util = util.util(debug, None)
        self.DICT = self.util.getDICT()
        self.plugins = [ ]
        self.load_plugins()
        self.reset()

    def do_analysis(self, data, rawbuf):
        pre_results = self.pre_scan(data)
        first_guess = self.deep_scan(pre_results, data)
        if (first_guess != None or len(first_guess) > 0):
            best_match = sorted(first_guess, key=lambda x: -x[1])
            readable_resaults = self.get_readable_results(best_match, data)
            if (len(readable_resaults) > 0):
                for p in self.plugins:
                    p.run(readable_resaults, best_match, data, rawbuf)

    def reset(self):
     self.first_approach = { }

    def load_plugins(self):
        if (self.debug):
            print ('checking for plugins...')
        pluginsfound = os.listdir(path.__plugindestination__)
        for plugin in pluginsfound:
            try:
                pluginpath = os.path.join(path.__plugindestination__, plugin)
                if (self.debug):
                    print ('loading and initialzing '+pluginpath)
                f, filename, description = imp.find_module('__init__', [pluginpath])
                self.plugins.append(imp.load_module(plugin, f, filename, description))
            except ImportError, err:
                print 'ImportError:', err

    def get_readable_results(self, best_match, data):
        # eliminate double entries
        matchpos = [ ]
        for match in best_match:
            if (match[0] not in matchpos):
                matchpos.append(match[0])
        clean_best_match = [ ]
        for pos in matchpos:
            for match in best_match:
                if (pos == match[0]):
                    clean_best_match.append(match)
                    break
        best_match = clean_best_match

        mapper = [ ]
        sorted_match = [ -1 ] * len(data)
        for i, bm in enumerate(best_match):
            # the following value defined the precision!
            if (bm[1] > 20 and sorted_match[bm[0]] == -1):
                wc = 0
                for a in range(bm[0], bm[0]+bm[3]):
                    if (bm[2] not in mapper and a < len(sorted_match)):
                        if (wc < 3):
                            sorted_match[a] = i
                        wc += 1
                mapper.append(bm[2])
        if (self.debug):
            print best_match
            print sorted_match

        readable_results = []
        last_word = ''
        for i in sorted_match:
            if (i >= 0):
                text_result = best_match[i][2]
                if (text_result != last_word):
                    readable_results.append(text_result)
                last_word = text_result

        return readable_results


    def deep_scan(self, pre_results, data):
        first_guess = [ ]
        for id in pre_results:
            results = pre_results[id]['results']
            l = pre_results[id]['l']
            startpos = self.get_start_pos(results)
            for pos in startpos:
                if (self.debug):
                    print ('searching for ' + id + ' between ' + str(pos) + ' and ' + str(pos+l))
                value = self.word_compare(id, pos, l, data)
                first_guess.append(value)
        return first_guess

    def word_compare(self, id, start, l, data):
        match_array = [ ]
        pos = 0
        points = 0
        match_factor = 0
        ll = 0
        for a in range(start, start+l):
            if (a < len(data)):                
                d = data[a]
                characteristic, meta = d
                if (characteristic != None):
                    characteristic_fft_approach = characteristic['fft_approach']
                    characteristic_tendency = characteristic['tendency']
                    o = self.fast_token_compare(characteristic_fft_approach, characteristic_tendency, id, match_array, pos)
                    point, ll = o
                    match_factor += point
                    pos += 1
        perfect_matches = 0
        fuzzy_matches = 0
        for arr in match_array:
             for a in range(0, len(arr[0])):
                 if (arr[0][a] > 0):
                     perfect_matches += 1
                 if (arr[1][a] > 0):
                     fuzzy_matches += 1
             #current_points = (sum(arr[0]) * perfect_matches) + (sum(arr[1]) * fuzzy_matches)
             #points += ((perfect_matches + fuzzy_matches) * current_points) / len(arr[0])
             points += sum(arr[0]) + sum(arr[1])
        factor = ll * len(match_array)
        if (factor > 0):
            points = points / factor
        else:
            points = 0
        perfect_points = sum(globalvars.IMPORTANCE)
        points = (points * 100 ) / perfect_points
        if (ll > 0):
           match_factor = match_factor / ll
           points = match_factor * points / 100
        else:
            points = 0
        if (self.debug):
            print id, start, points
        value = [start, points, id, ll, match_array]
        return value

    def get_start_pos(self, results):
        # TODO: Optimize start pos detection, for the time beeing we add zero to check from the very beginning as a kind of default
        startpos = [ ]
        #av = sum(results)/len(results)
        for i, result in enumerate(results):
            if (result >= 0): # av
                if (i not in startpos):
                    startpos.append(i)
        return startpos
            
    def pre_scan(self, data):
        pre_results = { }
        for i, d in enumerate(data):
            characteristic, meta = d
            if (characteristic != None):
                characteristic_fft_approach = characteristic['fft_approach']
                self.guess_word_start(characteristic_fft_approach, i, pre_results)
        return pre_results

    def guess_word_start(self, characteristic_fft_approach, pos, pre_results):
        for dict_entries in self.DICT['dict']:
             id = dict_entries['id']
             dict_characteristic = dict_entries['characteristic']
             dict_characteristic_tokens = dict_characteristic['tokens']
             match = 0
             l = len(dict_characteristic_tokens)
             for a, dict_characteristic_token in enumerate(dict_characteristic_tokens):
                 dict_characteristic_ffts = dict_characteristic_token['fft_approach']
                 for dict_characteristic_fft_approach in dict_characteristic_ffts:
                     match += self.fast_fft_scan(characteristic_fft_approach, dict_characteristic_fft_approach)
             if (id not in pre_results):
                 pre_results[id] = { 'results': [ match ], 'l': l }
             else:
                 pre_results[id]['results'].append( match )

    def fast_fft_scan(self, cfft, dfft):
        perfect_match_array = [0] * len(globalvars.IMPORTANCE)
        self.compare_fft_token_approach(cfft, dfft, perfect_match_array, [])
        perfect_matches = 0
        for pm in perfect_match_array:
            if (pm > 0):
                perfect_matches += 1
        return perfect_matches
             
    def fast_token_compare(self, characteristic_fft_approach, characteristic_tendency, id, match_array, pos):
        match = 0
        ll = 0
        for dict_entries in self.DICT['dict']:
            if (dict_entries['id'] == id):
                dict_characteristic = dict_entries['characteristic']
                dict_characteristic_tokens = dict_characteristic['tokens']
                ll = len(dict_characteristic_tokens)
                for i, dict_characteristic_token in enumerate(dict_characteristic_tokens):
                     if (i == pos):
                         dict_characteristic_ffts = dict_characteristic_token['fft_approach']
                         dict_tendency = dict_characteristic_token['tendency']
                         match += self.compare_tendency(characteristic_tendency, dict_tendency)
                         perfect_match_array = [0] * len(globalvars.IMPORTANCE)
                         fuzzy_array = [0] * len(globalvars.IMPORTANCE)
                         for dict_characteristic_fft_approach in dict_characteristic_ffts:
                             self.compare_fft_token_approach(characteristic_fft_approach, dict_characteristic_fft_approach, perfect_match_array, fuzzy_array)
                         match_array.append([perfect_match_array, fuzzy_array])
        return match, ll

    def compare_fft_token_approach(self, cfft, dfft, perfect_match_array, fuzzy_array):
        zipped = zip(cfft, dfft)
        lz = len(zipped)
        cut = len(globalvars.IMPORTANCE)
        for i, z in enumerate(zipped):
            a, b = z
            if (a < cut):
                factor = 1
                if (a == b):
                    if (a < len(globalvars.IMPORTANCE)):
                        factor = globalvars.IMPORTANCE[a]
                    if (a < len(perfect_match_array)):
                        perfect_match_array[a] += factor
                elif (b in cfft):
                    r = 0
                    f = cfft.index(b)
                    if (b < len(globalvars.IMPORTANCE)):
                        factor = globalvars.IMPORTANCE[b]
                    if (b < len(globalvars.WITHIN_RANGE)):
                        r = globalvars.WITHIN_RANGE[b]
                    if (i >= f - r and i <= f + r):
                        if (b < len(fuzzy_array)):
                            if (i > f):
                                factor = i - f
                            else:
                                factor = f - i
                            fuzzy_array[b] += factor

    def compare_tendency(self, c, d):
        convergency = 0
        if (c['len'] >= d['len_min'] and c['len'] <= d['len_max']):
            convergency += 25
        if (c['peaks'] >= d['peaks_min'] and c['peaks'] <= d['peaks_max']):
            convergency += 25
        if (c['avg'] >= d['avg_min'] and c['avg'] <= d['avg_max']):
            convergency += 25
        if (c['delta'] >= d['delta_min'] and c['delta'] <= d['delta_max']):
            convergency += 25
        return convergency
