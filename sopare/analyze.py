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
        self.dict_analysis = self.util.compile_analysis()
        self.load_plugins()
        self.first_approach = { }
        self.reset()

    def do_analysis(self, data, rawbuf):
        pre_results = self.pre_scan(data)
        print pre_results
        if (len(pre_results) < 2):
            return
        first_guess = self.first_scan(pre_results)
        print first_guess
        deep_guess = self.deep_scan(first_guess, data)
        print deep_guess
        if (deep_guess != None):
            best_match = sorted(deep_guess, key=lambda x: -x[1])
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
            if (bm[1] >= 80 and sorted_match[bm[0]] == -1):
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

    def deep_scan(self, first_guess, data):
        deep_guess = [ ]
        for id in first_guess:
            results = first_guess[id]['results']
            l = first_guess[id]['l']
            for pos in results:
                if (self.debug):
                    print ('searching for ' + id + ' between ' + str(pos) + ' and ' + str(pos+l))
                value = self.word_compare(id, pos, l, data)
                deep_guess.append(value)
        return deep_guess

    def first_scan(self, pre_results):
        first_guess = { }
        l = len(pre_results)
        for i, start in enumerate(pre_results):
            if (i+1 < l):
                # now comparing all dict entries from start to end
                end = pre_results[i+1]
                self.fast_compare(start, end, first_guess)
        return first_guess
                
    def fast_compare(self, start, end, first_guess):
        # we want to potential matching words and positions just by comparing
        # the tokens/word length
        l = (end-start)+1
        for id in self.dict_analysis:
            analysis_object = self.dict_analysis[id]
            potential_start_pos = [ ]
            if (self.debug):
                print ('checking for potential word ' + id + ' between ' + str(start) + ' and ' + str(end))
            print l, analysis_object['min_tokens'], analysis_object['max_tokens']
            if (l >= analysis_object['min_tokens']):
                c = 0
                for a in range(start, end):
                    if (c + l <= analysis_object['max_tokens']):
                        potential_start_pos.append(a)
                    c += 1
                if (id not in first_guess):
                    first_guess[id] = { 'results': potential_start_pos, 'l': l }
                else:
                    first_guess[id]['results'].extend( potential_start_pos )
        print first_guess

    def word_compare(self, id, start, l, data):
        match_array = [ ]
        pos = 0
        points = 0
        for a in range(start, start+l):
            if (a < len(data)):                
                d = data[a]
                characteristic, meta = d
                if (characteristic != None):
                    tendency = characteristic['tendency']
                    fft_approach = characteristic['fft_approach']
                    points += self.token_compare(tendency, fft_approach, id, pos, match_array)
                    pos += 1
        points = self.calculate_points(id, start, points, match_array, l)
        value = [start, points, id, l, match_array]
        return value

    def calculate_points(self, id, start, points, match_array, l):
        perfect_matches = 0
        fuzzy_matches = 0
        for arr in match_array:
            perfect_matches += sum(arr[0])
            fuzzy_matches += sum(arr[1])
        matches_sum = sum(globalvars.IMPORTANCE)
        match = (perfect_matches + fuzzy_matches) / l
        match = match * 100 / (matches_sum * l)
        if (points > 0):
            points = points / l
            points = match * points / 100
        else:
            points = match / (l*2)
        return points

    def pre_scan(self, data):
        startpos = [ ]
        cc = 0
        ws = True
        for d in data:
            characteristic, meta = d
            for m in meta:
                token = m['token']
                if (token != 'stop'):
                    if (token == 'silence/token end'):
                        ws = True
            if (characteristic != None):
                if (ws == True):
                    startpos.append(cc)
                    ws = False
                cc += 1
        if (len(startpos) == 1 and startpos[0] == 0):
            startpos.append(cc)
        return startpos

    def token_compare(self, tendency, fft_approach, id, pos, match_array):
        perfect_match_array = [0] * len(globalvars.IMPORTANCE)
        fuzzy_array = [0] * len(globalvars.IMPORTANCE)
        hct = 0
        for dict_entries in self.DICT['dict']:
            did = dict_entries['id']
            if (id == did):
                for i, characteristic in enumerate(dict_entries['characteristic']):
                    if (pos == i):
                        dict_tendency = characteristic['tendency']
                        hc = self.compare_tendency(tendency, dict_tendency)
                        if (hc > hct):
                            hct = hc
                        dict_fft_approach = characteristic['fft_approach']
                        self.compare_fft_token_approach(fft_approach, dict_fft_approach, perfect_match_array, fuzzy_array)
        match_array.append([perfect_match_array, fuzzy_array])
        return hct

    def compare_fft_token_approach(self, cfft, dfft, perfect_match_array, fuzzy_array):
        zipped = zip(cfft, dfft)
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
        if (c['len'] == d['len']):
            convergency += 40
        else:
            convergency -= 30
        if (c['peaks'] >= d['peaks']):
            convergency += 10
        else:
            convergency -= 5
        if (c['avg'] >= d['avg']):
            convergency += 40
        else:
            convergency -= 30
        if (c['delta'] >= d['delta']):
            convergency += 10
        else:
            convergency -= 5
        return convergency
