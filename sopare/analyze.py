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
        self.dict_analysis = self.util.compile_analysis(self.DICT)
        if (config.COMPRESS_DICT):
            self.DICT = self.util.compress_dict(self.DICT)
        self.plugins = [ ]
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
        if (self.debug):
            print ('deep_guess :' +str(deep_guess))
        if (deep_guess != None):
            best_match = self.get_best_match(deep_guess, startpos)
            if (self.debug):
                print ('best_match : '+ str(best_match))
            pre_readable_results = self.prepare_readable_results(best_match)
            if (self.debug):
                print ('pre_readable_results :'+str(pre_readable_results))
            readable_results = self.get_readable_results(pre_readable_results, data)
            if (self.debug):
                print ('readable_results :'+str(readable_results))
            if (len(readable_results) > 0):
                for p in self.plugins:
                    p.run(readable_results, best_match, data, word_tendency, rawbuf)

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

    def get_best_match(self, deep_guess, startpos):
        best_match = { }
        for guess in deep_guess:
            id = guess[0]
            pos = guess[1]
            ll = len(guess[2])
            if (id not in best_match):
                best_match[id] =  [ [ 0 ] * len(startpos), [ 0 ] * len(startpos) ]
            for i, point in enumerate(guess[2]):
                if (point[0] > config.MARGINAL_VALUE):
                    best_match[id][0][pos+i] += point[0]
                    best_match[id][1][pos+i] += point[1]
        return best_match

    def prepare_readable_results(self, best_match):
        pre_results = None
        readable_match = None
        readable_match_weighting = None
        for id in best_match:
            if (pre_results == None):
                pre_results = [ '' ] * len(best_match[id][0])
            if (readable_match == None):
                readable_match = [ 0 ] * len(best_match[id][0])
            if (readable_match_weighting == None):
                readable_match_weighting = [ 0 ] * len(best_match[id][0])
            for i, match in enumerate(best_match[id][0]):
                if (match > readable_match[i] and match > config.MIN_READABLE_RESULT_VALUE):
                    readable_match[i] = match
                    pre_results[i] = id
                readable_match_weighting[i] = best_match[id][1][i]
        if (pre_results != None):
            for i, result in enumerate(pre_results):
                if (i > 0 and i < len(pre_results)-1):
                    if (result != pre_results[i-1] and result != pre_results[i+1] and pre_results[i-1] == pre_results[i+1]):
                        if (self.debug):
                            print ('found enclosed element '+result+' at position '+str(i)+ ' ... replacing it with '+pre_results[i-1])
                        pre_results[i] = pre_results[i-1]
        return pre_results

    def get_readable_results(self, pre_results, data):
        readable_results = [ ] 
        if (pre_results == None):
            return readable_results
        last = ''
        start = 0
        count = 1
        for i, result in enumerate(pre_results):
            if (result != '' and last == result and i < len(pre_results)-1):
                count += 1
            else:
                if (i == len(pre_results)-1 and last == result):
                    count += 1
                if (last in self.dict_analysis and count >= self.dict_analysis[last]['min_tokens'] and count <= self.dict_analysis[last]['max_tokens']):
                    # TODO: instead if the word_shape_check we shoulc check that we get at least one token weighting > .9!
                    readable_results.append(last)
                elif (last != '' and self.debug):
                    print ('get_readable_results failed for '+ last +' cause '+str(self.dict_analysis[last]['min_tokens']) + ' < ' +str(count) + ' > '+str(self.dict_analysis[last]['max_tokens']))
                count = 1
                start = i
            last = result
        return readable_results

    def word_shape_check(self, start, count, id, data):
        word_shape = [ ]
        counter = 0
        for x in range(start, len(data)):
            d = data[x]
            characteristic, meta = d
            if (characteristic != None):
                counter += 1
                for m in meta:
                    if ('token_peaks' in m):
                        word_shape.extend(m['token_peaks'])
            if (counter >= count):
                break
        max_shape_similarity = 0
        for shape in self.dict_analysis[id]['shape']:
            shape_similarity = self.util.approach_length_similarity(word_shape, shape)
            if (shape_similarity > max_shape_similarity):
                max_shape_similarity = shape_similarity
            if (shape_similarity > config.SHAPE_SIMILARITY):
                return True
        if (self.debug):
            print ('Word shape check failed for '+ id +' at pos '+str(start) + '. Max was :'+str(max_shape_similarity))
        return False
 
    def deep_scan(self, first_guess, data):
        deep_guess = [ ]
        for id in first_guess:
            results = first_guess[id]['results']
            lmax = first_guess[id]['lmax']
            lmin = first_guess[id]['lmin']
            for i, pos in enumerate(results):
                if (self.debug):
                   if (i == 0):
                        print ('searching for ' + id + ' between ' + str(pos) + ' and ' + str(pos+lmax)),
                   else:
                        print (', ' + str(pos) + ' and ' + str(pos+lmax)),
                        if (i == len(results)-1):
                            print
                value = self.word_compare(id, pos, lmin, lmax, data)
                if (value != None):
                    deep_guess.append(value)
                else:
                    if (self.debug):
                        print (id + ' at ' + str(pos) + ' did not pass word_compare')
        return deep_guess

    def first_scan(self, pre_results, word_tendency, data):
        first_guess = { }
        for start in range(0, word_tendency['peaks']):
            for end in xrange(word_tendency['peaks'], 0, -1):
                for id in self.dict_analysis:
                    if (id not in first_guess):
                        p = end - start
                        if (p >= self.dict_analysis[id]['min_peaks'] and p <= self.dict_analysis[id]['max_peaks']):
                            peak_length = sum(word_tendency['peak_length'][start: start+p])
                            for a in range(0, len(self.dict_analysis[id]['min_peak_length']), 1):
                                mipl = self.dict_analysis[id]['min_peak_length'][a]
                                mapl = self.dict_analysis[id]['max_peak_length'][a]
                                if (peak_length >= mipl and peak_length <= mapl):
                                    first_guess[id] = { 'results': [], 'lmin': self.dict_analysis[id]['min_tokens'], 'lmax': self.dict_analysis[id]['max_tokens'] }
        if (not first_guess):
            if (self.debug):
                print ('first guess got no results ... now adding all dict entries!') # TODO: We need something better
            for id in self.dict_analysis:
                first_guess[id] = { 'results': [], 'lmin': self.dict_analysis[id]['min_tokens'], 'lmax': self.dict_analysis[id]['max_tokens'] }
        for words in pre_results:
            for startword in words:
                for id in first_guess:
                    if (startword not in first_guess[id]['results']):
                        if (self.fast_high_compare(id, startword, data) > 0 and self.word_shape_check(startword, first_guess[id]['lmax'], id, data)):
                            first_guess[id]['results'].append( startword )
        return first_guess

    def fast_high_compare(self, id, start, data):
        d = data[start]
        characteristic, meta = d
        if (characteristic != None):
            h = self.characteristic.get_highest(characteristic['fft_max'], config.FAST_HIGH_COMPARISON)
            hi = self.characteristic.get_highest(characteristic['fft_approach'], config.FAST_HIGH_COMPARISON)
            analysis_object = self.dict_analysis[id]
            for o in analysis_object['high5']:
                dhi, dh = o
                dh = self.characteristic.get_highest(dh, config.FAST_HIGH_COMPARISON)
                intersection = self.util.approach_intersection(hi, dhi)
                if (len(intersection) > 0):
                    if (self.util.approach_similarity(h, dh) > config.FAST_HIGH_COMPARE_MARGINAL_VALUE):
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
                    self.token_compare(id, pos, characteristic, match_array)
                    pos += 1
        points = self.calculate_points(id, start, match_array, lmin, lmax)
        return [id, start, points]

    def calculate_points(self, id, start, match_array, lmin, lmax):
        points = [ ]
        got_matches_for_all_tokens = 0
        ll = len(match_array)
        if (ll < lmin):
            return [ 0 ], [ 0 ]
        for i, arr in enumerate(match_array):
            if (config.USE_FUZZY):
                arr[0] = self.make_fuzzy(arr[0], arr[1])
            high_matches = self.get_high_matches(arr[0])
            perfect_match_sum = sum(arr[0])
            perfect_match_sum_check = sum(config.IMPORTANCE[0:len(arr[0])])
            fft_similarity = self.get_similarity(arr[2], 'fft_similarity')
            tendency_similarity = self.get_similarity(arr[2], 'tendency_similarity')
            outline_distance = self.get_similarity(arr[2], 'outline_distance')
            weighting = self.get_weighting(arr[2])
            point = fft_similarity * config.FFT_SIMILARITY 
            point += tendency_similarity * config.TENDENCY_SIMILARITY
            if (outline_distance > 100):
                outline_distance = 100
            outline_distance = (100-outline_distance) / 100
            point += outline_distance * config.OUTLINE_DISTANCE
            high_match_points = (high_matches * 100 / 5) / 100
            point += high_match_points * config.HIGH_MATCH_POINTS 
            match_points = (perfect_match_sum * 100 / perfect_match_sum_check) / 100
            point += match_points * config.MATCH_POINTS
            points.append([round(point,2), weighting])
        return points

    def get_weighting(self, arr):
        weighting = 0
        counter = 0
        for s in arr:
            weighting += s['weighting']
            counter += 1.0
        return weighting/counter

    def get_similarity(self, arr, field):
        similarity_max = 0
        for similarity in arr:
            v = similarity[field]
            if (v > similarity_max):
                similarity_max = v
        return similarity_max

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
                if (len(word) > 0 and len(word) < 10 and word not in wordpos): # TODO: make max. word length configurable
                    wordpos.append(word)
        else:
            wordpos.append(endpos)
        if (self.debug):
            print ('wordpos : '+str(wordpos))
        return wordpos, endpos

    def token_compare(self, id, pos, characteristic, match_array):
        perfect_match_array = [0] * len(config.IMPORTANCE)
        fuzzy_array = [0] * len(config.IMPORTANCE)
        similarity_array = [ ]
        for dict_entries in self.DICT['dict']:
            did = dict_entries['id']
            if (id == did and pos < len(dict_entries['characteristic'])):
                tendency = characteristic['tendency']
                fft_approach = characteristic['fft_approach']
                fft_max = characteristic['fft_max']
                fft_freq = characteristic['fft_freq']
                fft_outline = characteristic['fft_outline']
                dict_tendency = dict_entries['characteristic'][pos]['tendency']
                dict_fft_freq = dict_entries['characteristic'][pos]['fft_freq']
                tendency_similarity = self.util.approach_similarity(
                 [fft_freq, tendency['len'], tendency['avg'], tendency['delta'], tendency['deg'] ],
                 [dict_fft_freq, dict_tendency['len'], dict_tendency['avg'], dict_tendency['delta'], dict_tendency['deg']]
                )
                dict_fft_approach = dict_entries['characteristic'][pos]['fft_approach']
                dict_fft_max = dict_entries['characteristic'][pos]['fft_max']
                dict_fft_outline = dict_entries['characteristic'][pos]['fft_outline']
                fft_similarity = self.util.approach_similarity(fft_max, dict_fft_max)
                if (config.USE_LENGTH_SIMILARITY):
                    fft_length_similarity = self.util.approach_length_similarity(fft_max, dict_fft_max)
                    fft_similarity = fft_similarity * fft_length_similarity
                perfect_match_array, fuzzy_array = self.compare_fft_token_approach(fft_approach, dict_fft_approach, perfect_match_array, fuzzy_array)
                fft_outline.sort(reverse=True)
                dict_fft_outline.sort(reverse=True)
                outline_distance = self.util.approach_distance(fft_outline, dict_fft_outline)
                if (config.POSITION_WEIGHTING):
                    fft_similarity = fft_similarity * (1-pos*.1)
                similarity_array.append({ 'tendency_similarity': tendency_similarity, 'fft_similarity': fft_similarity, 'outline_distance': outline_distance, 'weighting': dict_entries['characteristic'][pos]['weighting'] })
        match_array.append([perfect_match_array, fuzzy_array, similarity_array])

    def compare_fft_token_approach(self, cfft, dfft, perfect_match_array, fuzzy_array):
        zipped = zip(cfft, dfft)
        cut = len(config.IMPORTANCE)
        if (len(zipped) < cut):
            cut = len(zipped)
            perfect_match_array = perfect_match_array[0:cut]
            fuzzy_array = fuzzy_array[0:cut]
        for i,z in enumerate(zipped):
            a, b = z
            if (a < cut):
                factor = 1
                if (a == b):
                    factor = config.IMPORTANCE[a]
                    if (a < len(perfect_match_array) and perfect_match_array[a] == 0):
                        perfect_match_array[a] = factor
                elif (b in cfft):
                    r = 0
                    g = cfft.index(b)
                    factor = config.IMPORTANCE[g]
                    if (g < len(config.WITHIN_RANGE)):
                        r = config.WITHIN_RANGE[g]
                    if (i >= g - r and i <= g + r):
                        if (b < len(fuzzy_array) and fuzzy_array[b] == 0):
                            fuzzy_array[b] = factor
        return perfect_match_array, fuzzy_array
