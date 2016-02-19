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
        pre_results, word_tendencies = self.pre_scan(data)
        if (self.debug):
            print ('pre_results : '+str(pre_results))
        if (pre_results == None):
            return
        first_guess = self.first_scan(pre_results, word_tendencies, data)
        if (self.debug):
            print ('first_guess : ' + str(first_guess))
        deep_guess = self.deep_scan(first_guess, data)
        if (deep_guess != None):
            best_match = sorted(deep_guess, key=lambda x: -x[1])
            if (self.debug):
                print ('best_match : '+ str(best_match))
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
            if (bm[1] >= 1 and sorted_match[bm[0]] == -1):
                wc = 0
                for a in range(bm[0], bm[0]+bm[3]):
                    if (bm[2] not in mapper and a < len(sorted_match)):
                        if (wc < 3):
                            sorted_match[a] = i
                        wc += 1
                mapper.append(bm[2])
        if (self.debug):
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
            lmax = first_guess[id]['lmax']
            lmin = first_guess[id]['lmin']
            for pos in results:
                if (self.debug):
                    print ('searching for ' + id + ' between ' + str(pos) + ' and ' + str(pos+lmax))
                value = self.word_compare(id, pos, lmin, lmax, data)
                if (value != None):
                    deep_guess.append(value)
        return deep_guess

    def first_scan(self, pre_results, word_tendencies, data):
        first_guess = { }
        word_tendency = None
        for a, words in enumerate(pre_results):
            if (len(pre_results) == len(word_tendencies)):
                word_tendency = word_tendencies[a]
            else:
                word_tendency = None
            for i, start in enumerate(words):
                d = data[start]
                characteristic, meta = d
                tendency = characteristic['tendency']
                self.fast_compare(i, start, len(words), word_tendency, first_guess)
        if not first_guess:
            print ('TODO: WE NEED A MORE LIBERAL LETHOD TO FILL first_guess ...')
        return first_guess
                
    def fast_compare(self, i, start, word_len, word_tendency, first_guess):
        # we want to find potential matching words and positions 
        # based on a rough pre comparison
        for id in self.dict_analysis:
            analysis_object = self.dict_analysis[id]
            if ((word_tendency == None or (word_tendency['peaks'] >= analysis_object['min_peaks'] and word_tendency['peaks'] <= analysis_object['max_peaks']))
             and (i == 0 or (start + analysis_object['min_tokens']) <= word_len)):
                if (id not in first_guess):
                    first_guess[id] = { 'results': [ start ], 'lmin': analysis_object['min_tokens'], 'lmax': analysis_object['max_tokens'] }
                else:
                    first_guess[id]['results'].append( start )

    def word_compare(self, id, start, lmin, lmax, data):
        match_array = [ ]
        pos = 0
        points = 0
        for a in range(start, start+lmax):
            if (a < len(data)):                
                d = data[a]
                characteristic, meta = d
                if (characteristic != None):
                    tendency = characteristic['tendency']
                    fft_approach = characteristic['fft_approach']
                    fft_avg = characteristic['fft_avg']
                    fft_freq = characteristic['fft_freq']
                    points += self.token_compare(tendency, fft_approach, fft_avg, fft_freq, id, pos, match_array)
                    pos += 1
        points = self.calculate_points(id, start, points, match_array, lmin, lmax)
        if (points == 0):
            return None
        value = [start, points, id, lmax, match_array]
        return value

    def calculate_points(self, id, start, points, match_array, lmin, lmax):
        ll = len(match_array)
        match_array_counter = 0
        best_match = 0
        best_match_h = 0
        perfect_matches = 0
        perfect_match_sum = 0
        points = points / ll
        if (points > 100):
            points = 100
        got_matches_for_all_tokens = 0
        for arr in match_array:
            best_match_h = sum(arr[0])
            if (best_match_h > 2): # avoid false positives, TODO: Make configurable
                best_match_h += sum(arr[1])
                got_matches_for_all_tokens += 1
            if (best_match_h > best_match):
                check = sum(globalvars.IMPORTANCE[0:len(arr[0])])
                best_match = best_match_h
                perfect_matches += best_match
                perfect_match_sum += check
        if (got_matches_for_all_tokens < len(match_array)):
            if (self.debug):
                print ('dumping score because of token matches '+str(got_matches_for_all_tokens) + ' ! ' + str(len(match_array)))
            perfect_matches = perfect_matches * got_matches_for_all_tokens / len(match_array)
        if (len(match_array) < lmin or len(match_array) > lmax):
            if (self.debug):
                 print ('this seems to be a false positive as min/max token length does not match :'+str(lmin) + ' < ' + str(len(match_array))+ ' > ' + str(lmax))
            perfect_matches = perfect_matches / 10
        if (perfect_match_sum > 0):
            perfect_matches = perfect_matches * 100 / perfect_match_sum 
            if (perfect_matches > 100):
                perfect_matches = 100
            best_match = perfect_matches * points / 100
            if (ll >= lmin and ll <= lmax):
                if (self.debug):
                    print ('-------------------------------------')
                    print ('id/start/points/perfect_matches/best_match ' + id + '/' + str(start) + '/' + str(points) + '/' + str(perfect_matches) + '/' + str(best_match))
                return best_match
            else:
                if (self.debug):
                    print ('----------- !!! '+str(ll) +' >= '+str(lmin) + ' and ' +str(ll) + ' <= ' + str(lmax))
        else:
            if (self.debug):
    	        print ('----------- perfect_match_sum == 0')
        return 0

    def pre_scan(self, data):
        startpos = [ ]
        endpos = [ ]
        word_tendencies = [ ]
        for i, d in enumerate(data):
            characteristic, meta = d
            if (characteristic != None):
                startpos.append(i)
        for i, d in enumerate(data):
            characteristic, meta = d
            for m in meta:
                token = m['token']
                if (token != 'stop'):
                    if (token == 'word'):
                        endpos.append(i)
                    if ('word_tendency' in m):
                        word_tendencies.append(m['word_tendency'])
        if (len(endpos) > 0 and len(startpos) > 0):
            new_startpos = [ ]
            last = 0
            for end in endpos:
                word_pos = [ ]
                for start in startpos:
                    if (start <= end and start > last):
                        word_pos.append(start)
                last = end
                if (len(word_pos) != 0):
                    new_startpos.append(word_pos)
            startpos = new_startpos
        else:
            startpos = [ ].append(startpos)
        return startpos, word_tendencies

    def token_compare(self, tendency, fft_approach, fft_avg, fft_freq, id, pos, match_array):
        perfect_match_array = [0] * len(globalvars.IMPORTANCE)
        fuzzy_array = [0] * len(globalvars.IMPORTANCE)
        hct = 0
        counter = 0
        for dict_entries in self.DICT['dict']:
            did = dict_entries['id']
            if (id == did):
                analysis_object = self.dict_analysis[id]
                for i, characteristic in enumerate(dict_entries['characteristic']):
                    if (pos == i):
                        dict_tendency = characteristic['tendency']
                        hc = self.compare_tendency(tendency, dict_tendency, fft_freq, characteristic['fft_freq'])
                        if (hc > hct):
                            hct = hc
                        dict_fft_approach = characteristic['fft_approach']
                        dict_fft_avg =  characteristic['fft_avg']
                        min_fft_avg = analysis_object['min_fft_avg'][pos]
                        max_fft_avg = analysis_object['max_fft_avg'][pos]
                        perfect_match_array, fuzzy_array = self.compare_fft_token_approach(fft_approach, dict_fft_approach, fft_avg, dict_fft_avg, min_fft_avg, max_fft_avg, perfect_match_array, fuzzy_array)
                        counter += 1
        match_array.append([perfect_match_array, fuzzy_array])
        return hct

    def compare_fft_token_approach(self, cfft, dfft, fft_avg, dict_fft_avg, min_fft_avg, max_fft_avg, perfect_match_array, fuzzy_array):
        zipped = zip(cfft, dfft, fft_avg, min_fft_avg, max_fft_avg, dict_fft_avg)
        cut = len(globalvars.IMPORTANCE)
        if (len(zipped) < cut):
            cut = len(zipped)
            perfect_match_array = perfect_match_array[0:cut]
            fuzzy_array = fuzzy_array[0:cut]
        for i, z in enumerate(zipped):
            a, b, c, d, e, f = z
            if (a < cut):
                factor = 1
                if (a == b and c >= d and c <= e):
                    c_range = c * 20 / 100 # 20%
                    if (a < len(globalvars.IMPORTANCE)):
                        factor = globalvars.IMPORTANCE[a]
                    if (a < len(perfect_match_array) and perfect_match_array[a] == 0 and c - c_range <= f and c + c_range >= f):
                        perfect_match_array[a] = factor
                elif (b in cfft):
                    r = 0
                    g = cfft.index(b)
                    c = fft_avg[g]
                    c_range = c * 20 / 100 # 20%
                    factor = 1
                    if (g < len(globalvars.IMPORTANCE)):
                        factor = globalvars.IMPORTANCE[g]
                    if (g < len(globalvars.WITHIN_RANGE)):
                        r = globalvars.WITHIN_RANGE[g]
                    if (i >= g - r and i <= g + r and c >= d and c <= e and c - c_range <= f and c + c_range >= f):
                        if (b < len(fuzzy_array) and fuzzy_array[b] == 0):
                            fuzzy_array[b] = factor
        return perfect_match_array, fuzzy_array

    def compare_tendency(self, c, d, cfreq, dfreq):
        convergency = 0
        if (c['len'] == d['len']):
            convergency += 30
        else:
            convergency -= 15
        if (c['peaks'] >= d['peaks']):
            convergency += 10
        else:
            convergency -= 5
        if (c['avg'] >= d['avg']):
            convergency += 30
        else:
            convergency -= 15
        if (c['delta'] >= d['delta']):
            convergency += 10
        else:
            convergency -= 5
        if (cfreq == dfreq):
            convergency = convergency + 20
        else:
            convergency = convergency - 10
        return convergency
