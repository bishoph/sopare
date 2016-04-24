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
import path
import util
import imp
import os

class analyze():

    def __init__(self, debug):
        self.debug = debug
        self.characteristic = characteristics.characteristic(debug)
        self.util = util.util(debug, None)
        self.DICT = self.util.getDICT()
        self.plugins = [ ]
        self.dict_analysis = self.util.compile_analysis()
        self.load_plugins()
        self.first_approach = { }
        self.reset()

    def do_analysis(self, data, word_tendency, rawbuf):
        pre_results, startpos = self.pre_scan(data, word_tendency)
        if (self.debug):
            print ('pre_results : '+str(pre_results))
        if (pre_results == None):
            return
        first_guess = self.first_scan(pre_results, word_tendency, data)
        if (self.debug):
            print ('first_guess : ' + str(first_guess))
        deep_guess = self.deep_scan(first_guess, data)
        if (deep_guess != None):
            best_match = sorted(deep_guess, key=lambda x: -x[1])
            if (self.debug):
                print ('best_match : '+ str(best_match))
            readable_resaults = self.get_readable_results(best_match, pre_results, first_guess, startpos, data)
            if (len(readable_resaults) > 0):
                for p in self.plugins:
                    p.run(readable_resaults, best_match, data, word_tendency, rawbuf)

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

    def get_readable_results(self, best_match, pre_results, first_guess, startpos, data):
        readable_results = [ ]
        mapper = [ '' ] * len(startpos)
        for match in best_match:
            self.mapword(match, mapper, startpos)
        if (self.debug):
            print ('mapper :'+str(mapper))
        for match in mapper:
            if (self.verify_matches(first_guess, match)):
                if (match not in readable_results):
                    readable_results.append(match)
        return readable_results

    def verify_matches(self, first_guess, match):
        for guess in first_guess:
            if (guess == match):
                if ('tokencount' not in first_guess[guess]):
                    first_guess[guess]['tokencount'] = 1
                else:
                    first_guess[guess]['tokencount'] += 1
                if (first_guess[guess]['tokencount'] >= first_guess[guess]['lmin'] and first_guess[guess]['tokencount'] <= first_guess[guess]['lmax']):
                    return True
        return False

    def mapword(self, match, mapper, startpos):
        sp = startpos.index(match[0])
        for a in range(sp, sp + match[5]):
            if (a < len(mapper) and mapper[a] == '' and match[1] >= config.MARGINAL_VALUE):
                mapper[a] = match[2]
 
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
                else:
                    if (self.debug):
                        print (id + ' at ' + str(pos) + ' did not pass word_compare')
        return deep_guess

    def first_scan(self, pre_results, word_tendency, data):
        # we want to find potential matching words and positions 
        # based on a rough pre comparison
        first_guess = { }
        word_possibilities = self.util.partition(word_tendency['peaks'])
        for id in self.dict_analysis:
            for pos, pset in enumerate(word_possibilities):
                for p in pset:
                    if (id not in first_guess):
                        if (p >= self.dict_analysis[id]['min_peaks'] and p <= self.dict_analysis[id]['max_peaks']):
                            peak_length = sum(word_tendency['peak_length'][pos: pos+p])
                            for a in range(0, len(self.dict_analysis[id]['min_peak_length']), 1):
                                mipl = self.dict_analysis[id]['min_peak_length'][a]
                                mapl = self.dict_analysis[id]['max_peak_length'][a]
                                if (peak_length >= mipl and peak_length <= mapl):
                                    first_guess[id] = { 'results': [], 'lmin': self.dict_analysis[id]['min_tokens'], 'lmax': self.dict_analysis[id]['max_tokens'] }
        for words in pre_results:
            for startword in words:
                for id in first_guess:
                    if (startword not in first_guess[id]['results']):
                        if (config.ALL_START_POS or self.fast_high_compare(id, startword, data) > 0):
                            first_guess[id]['results'].append( startword )
        return first_guess

    def fast_high_compare(self, id, start, data):
        d = data[start]
        characteristic, meta = d
        if (characteristic != None):
            fft_max = characteristic['fft_max']
            analysis_object = self.dict_analysis[id]
            hi, h = self.characteristic.get_highest(fft_max, config.FAST_HIGH_COMPARISON)
            hi_min = min(hi)
            hi_max = max(hi)
            for o in analysis_object['high5']:
                dhi, dh = o
                dhi_min = min(dhi)
                dhi_max = max(dhi)
                h_sum = sum(h)
                dh_sum = sum(dh)
                h_range = h_sum * config.INACCURACY_FAST_HIGH_COMPARE / 100
                if (h_sum - h_range <= dh_sum and h_sum + h_range >= dh_sum):
                    h_range = dhi_max * config.INACCURACY_FAST_HIGH_COMPARE / 100
                    if (dhi_min - h_range <= hi_min and dhi_min - h_range <= hi_max and dhi_max + h_range >= hi_min and dhi_max + h_range >= hi_max):
                        return 1
        return 0

    def word_compare(self, id, start, lmin, lmax, data):
        match_array = [ ]
        pos = 0
        for a in range(start, start+lmax):
            if (a < len(data)):
                d = data[a]
                characteristic, meta = d
                if (characteristic != None):
                    tendency = characteristic['tendency']
                    fft_approach = characteristic['fft_approach']
                    fft_max = characteristic['fft_max']
                    fft_freq = characteristic['fft_freq']
                    self.token_compare(tendency, fft_approach, fft_max, fft_freq, id, pos, match_array)
                    pos += 1
        points, got_matches_for_all_tokens = self.calculate_points(id, start, match_array, lmin, lmax)
        if (points > 0):
            return [start, points, id, lmax, match_array, got_matches_for_all_tokens]
        return None

    def calculate_points(self, id, start, match_array, lmin, lmax):
        points = 0
        got_matches_for_all_tokens = 0
        ll = len(match_array)
        tendency_match_sum = 0
        perfect_match_sum = 0
        check = 0
        for i, arr in enumerate(match_array):
            check += sum(config.IMPORTANCE[0:len(arr[0])])
            if (config.USE_FUZZY):
                arr[0] = self.make_fuzzy(arr[0], arr[1])
            h5 = self.get_high_matches(arr[0])
            tpp = 0
            tpn = 0
            for tp in arr[2]:
                if (tp > 0):
                    tpp += tp
                else:
                    tpn += tp
            if (h5 >= len(arr[0]) or h5 >= config.MIN_PERFECT_MATCHES_FOR_CONSIDERATION):
                 perfect_match_sum += sum(arr[0])
                 got_matches_for_all_tokens += 1
            tendency_match_sum += tpp+tpn
        percentage_match = 0
        if (perfect_match_sum > 0):
            percentage_match = 100 * perfect_match_sum / check
        if (got_matches_for_all_tokens > 0):
            percentage_match = percentage_match * got_matches_for_all_tokens / ll
        else:
            percentage_match = 0
        points = percentage_match + tendency_match_sum
        if (ll < lmin or ll > lmax):
            points = points / 2
        if (points > 100):
            points = 100
        return points, got_matches_for_all_tokens

    def make_fuzzy(self, arr, fuzzy):
        for x in range(0, len(arr)):
            if (fuzzy[x] > 0):
                arr[x] = fuzzy[x]
        return arr

    def get_high_matches(self, arr):
        high = 0
        ll = len(arr)
        if (ll > 5):
            ll = 5
        for x in range(0,ll):
            if (arr[x] > 0):
                high += 1
        return high

    def pre_scan(self, data, word_tendency):
        posmapper = [ ]
        startpos = [ ]
        endpos = [ ]
        peaks = [ ]
        for i, d in enumerate(data):
            characteristic, meta = d
            endpos.append(i)
            for m in meta:
                token = m['token']
                if (token != 'stop'):
                    if (token == 'token'):
                        posmapper.append(m['pos'])
                    elif (token == 'start analysis'):
                        posmapper.append(m['pos'])
        for sp in word_tendency['start_pos']:
            for i, pm in enumerate(posmapper):
                if (pm > sp):
                    startpos.append(i-1)
                    break
        wordpos = [ ]
        if (len(endpos) > 0 and len(startpos) > 0):
            for start in startpos:
                word = [ ]
                for end in endpos:
                    if (start <= end):
                        word.append(end)
                if (len(word) > 0 and word not in wordpos):
                    wordpos.append(word)
        else:
            wordpos.append(endpos)
        if (self.debug):
            print ('wordpos : '+str(wordpos))
        return wordpos, endpos

    def token_compare(self, tendency, fft_approach, fft_max, fft_freq, id, pos, match_array):
        perfect_match_array = [0] * len(config.IMPORTANCE)
        fuzzy_array = [0] * len(config.IMPORTANCE)
        tendency_array = [ ]
        negative = 0
        for dict_entries in self.DICT['dict']:
            did = dict_entries['id']
            if (id == did and pos < len(dict_entries['characteristic'])):
                dict_tendency = dict_entries['characteristic'][pos]['tendency']
                analysis_object = self.dict_analysis[id]
                hc = self.compare_tendency(tendency, dict_tendency, fft_freq, dict_entries['characteristic'][pos]['fft_freq'])
                if (hc > 0 and hc not in tendency_array):
                    tendency_array.append(hc)
                else:
                    negative += hc
                dict_fft_approach = dict_entries['characteristic'][pos]['fft_approach']
                dict_fft_max = dict_entries['characteristic'][pos]['fft_max']
                perfect_match_array, fuzzy_array = self.compare_fft_token_approach(fft_approach, dict_fft_approach, fft_max, dict_fft_max, perfect_match_array, fuzzy_array)
        if (sum(tendency_array) < 40): # TODO: Make configurable
            tendency_array.append(negative)
        match_array.append([perfect_match_array, fuzzy_array, tendency_array])

    def compare_fft_token_approach(self, cfft, dfft, fft_max, dict_fft_max, perfect_match_array, fuzzy_array):
        zipped = zip(cfft, dfft, fft_max, dict_fft_max)
        cut = len(config.IMPORTANCE)        
        if (len(zipped) < cut):
            cut = len(zipped)
            perfect_match_array = perfect_match_array[0:cut]
            fuzzy_array = fuzzy_array[0:cut]
        for i, z in enumerate(zipped):
            a, b, e, f = z
            if (a < cut):
                factor = 1
                e_range = e * config.INACCURACY / 100
                if (a == b and e - e_range <= f and e + e_range >= f):
                    if (a < len(config.IMPORTANCE)):
                        factor = config.IMPORTANCE[a]
                    if (a < len(perfect_match_array) and perfect_match_array[a] == 0):
                        perfect_match_array[a] = factor
                elif (b in cfft):
                    r = 0
                    g = cfft.index(b)
                    e_range = e * config.INACCURACY / 100
                    factor = 1
                    if (g < len(config.IMPORTANCE)):
                        factor = config.IMPORTANCE[g]
                    if (g < len(config.WITHIN_RANGE)):
                        r = config.WITHIN_RANGE[g]
                    if (i >= g - r and i <= g + r and e - e_range <= f and e + e_range >= f):
                        if (b < len(fuzzy_array) and fuzzy_array[b] == 0):
                            fuzzy_array[b] = factor
        return perfect_match_array, fuzzy_array

    def compare_tendency(self, c, d, cfreq, dfreq):
        convergency = 0
        range = c['len'] * config.INACCURACY / 100 # TODO: Check if we need a unique config option for this
        if (c['len'] - range <= d['len'] and c['len'] + range >= d['len']):
            convergency += 25
        else:
            convergency -= 2
        range = c['avg'] * config.INACCURACY / 100 # TODO: Check if we need a unique config option for this
        if (c['avg'] - range <= d['avg'] and c['avg'] + range >= d['avg']):
            convergency += 25
        else:
            convergency -= 2
        range = c['deg'] * config.TENDENCY_INACCURACY / 100
        if (c['deg'] - range <= d['deg'] and c['deg'] + range >= d['deg']):
            convergency += 50
        else:
            convergency -= 4
        return convergency
