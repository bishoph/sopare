
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

    def do_analysis(self, data):
        pre_results = self.pre_scan(data)
        print pre_results
        first_guess = self.deep_scan(pre_results, data)

    def deep_scan(self, first_guess, data):
        for id in first_guess:
            results = first_guess[id]['results']
            l = first_guess[id]['l']
            startpos = self.get_start_pos(results)
            for pos in startpos:
                if (self.debug):
                    print ('searching for ' + id + ' between ' + str(pos) + ' and ' + str(pos+l))
                self.word_compare(id, pos, l, data)

    def word_compare(self, id, start, l, data):
        match_array = [0] * len(globalvars.IMPORTANCE)
        pos = 0
        match = 0
        for a in range(start, start+l):
            if (a < len(data)):
                d = data[a]
                characteristic, meta = d
                if (characteristic != None):
                    characteristic_fft_approach = characteristic['fft_approach']
                    characteristic_tendency = characteristic['tendency']
                    match += self.fast_token_compare(characteristic_fft_approach, characteristic_tendency, id, match_array, pos)
                    pos += 1
        print id, start, sum(match_array), match

    def get_start_pos(self, results):
        startpos = [ ]
        m = max(results)
        for i, result in enumerate(results):
            if (result == m):
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
                     match += self.fast_fft_scan(characteristic_fft_approach, dict_characteristic_fft_approach, id, pos)
             if (id not in pre_results):
                 pre_results[id] = { 'results': [ match ], 'l': l }
             else:
                 pre_results[id]['results'].append( match )

    def fast_fft_scan(self, characteristic_fft_approach, dict_characteristic_fft_approach, id, pos):
        match = 0
        # We focus on the very first values to detect the word start
        check_range = len(globalvars.WITHIN_RANGE)
        for check in range(0, check_range):
            index_c = characteristic_fft_approach.index(check)
            index_d = dict_characteristic_fft_approach.index(check)
            r = globalvars.WITHIN_RANGE[check]
            if (index_c == index_d or (index_c >= index_d - r and index_c <= index_d + r)):
                match = match + 1
        return match
             
    def fast_token_compare(self, characteristic_fft_approach, characteristic_tendency, id, match_array, pos):
        match = 0
        for dict_entries in self.DICT['dict']:
            if (dict_entries['id'] == id):
                dict_characteristic = dict_entries['characteristic']
                dict_characteristic_tokens = dict_characteristic['tokens']
                for i, dict_characteristic_token in enumerate(dict_characteristic_tokens):
                     if (i == pos):
                         dict_characteristic_ffts = dict_characteristic_token['fft_approach']
                         dict_tendency = dict_characteristic_token['tendency']
                         match += self.compare_tendency(characteristic_tendency, dict_tendency)
                         for i, dict_characteristic_fft_approach in enumerate(dict_characteristic_ffts):
                             self.compare_fft_token_approach(characteristic_fft_approach, dict_characteristic_fft_approach, match_array)
        return match

    def compare_fft_token_approach(self, cfft, dfft, match_array):
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
                        match_array[a] += factor
                elif (b in cfft):
                    r = 0
                    f = cfft.index(b)
                    if (b < len(globalvars.IMPORTANCE)):
                        factor = globalvars.IMPORTANCE[b]
                    if (b < len(globalvars.WITHIN_RANGE)):
                        r = globalvars.WITHIN_RANGE[b]
                    if (i >= f - r and i <= f + r):
                        if (i > f):
                            factor = factor - (i - f)
                        else:
                            factor = factor - (f - i)
                        if (b < len(match_array)):
                            match_array[b] += factor

    def compare_tendency(self, c, d):
        convergency = 0
        if (c['len'] >= d['len_min'] and c['len'] <= d['len_max']):
            convergency += 50
        else:
            convergency -= 40
        if (c['peaks'] >= d['peaks_min'] and c['peaks'] <= d['peaks_max']):
            convergency += 15
        else:
            convergency -= 10
        if (c['avg'] >= d['avg_min'] and c['avg'] <= d['avg_max']):
            convergency += 30
        else:
            convergency -= 20
        if (c['delta'] >= d['delta_min'] and c['delta'] <= d['delta_max']):
            convergency += 5
        else:
            convergency -= 3
        return convergency
