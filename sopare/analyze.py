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
import operator
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
            print ('pre_results : ' + str(pre_results))
        if (pre_results == None):
            return
        first_guess = self.first_scan(pre_results, startpos, word_tendency, data)
        if (self.debug):
            print ('first_guess : ' + str(first_guess))
        first_token_weighting = self.analyze_first_token(first_guess, data)
        if (self.debug):
            print ('first_token_weighting : ' + str(first_token_weighting))
        weighted_results = self.weight_first_token(first_token_weighting, startpos)
        if (self.debug):
            print ('weighted_results : ' + str(weighted_results))
        deep_guess = self.deep_scan(weighted_results, data)
        if (self.debug):
            print ('deep_guess : ' + str(deep_guess))
        if (deep_guess != None):
            best_match = self.get_best_match(deep_guess, startpos)
            if (self.debug):
                print ('best_match : ' + str(best_match))
            pre_readable_results = self.prepare_readable_results(best_match, weighted_results)
            if (self.debug):
                print ('pre_readable_results : ' + str(pre_readable_results))
            boosted_results = self.get_boosted_results(pre_readable_results, pre_results)
            if (self.debug):
                print ('boosted_results : ' + str(boosted_results))
            validated_results =  self.validate_results(boosted_results, word_tendency, data)
            if (self.debug):
                print ('validated_result : ' + str(validated_results))
            readable_results = self.get_readable_results(validated_results, data)
            if (self.debug):
                print ('readable_results : ' + str(readable_results))
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
            if (id not in best_match):
                best_match[id] =  [ [ 0 ] * len(startpos), [ 0 ] * len(startpos) ]
            for i, point in enumerate(guess[2]):
                if (point[0] > config.MARGINAL_VALUE and pos+i < len(best_match[id][0])):
                    if (point[0] > best_match[id][0][pos+i]):
                         best_match[id][0][pos+i] = point[0]
                         best_match[id][1][pos+i] = point[1]
        best_result_list = [ ]
        for id in best_match:
            bms = sum(best_match[id][0])/len(best_match[id][0])
            if (bms >= config.BEST_MATCH_VALUE):
                best_result_list.append([id, bms])
        best_result_list = sorted(best_result_list, key=lambda x: x[1], reverse=True)
        return best_match

    def prepare_readable_results(self, best_match, weighted_results):
        # Building confidence and prepare pre_results
        confidence = { }
        for id in best_match:
            confidence[id] = { 'best_match_sum': sum(best_match[id][0]), 'count': 0, 'score': 0 }
        pre_results = None
        stacked_results = [ ]
        ll = 0
        for id in best_match:
            if (pre_results == None):
                ll = len(best_match[id][0])
                pre_results = [ '' ] * ll
            stack = [ '' ] * ll
            weighting = [ 0 ] * ll
            if (pre_results == None):
                ll = len(best_match[id][0])
                pre_results = [ '' ] * ll
            for i, match in enumerate(best_match[id][0]):
                if (config.POSITION_WEIGHTING):
                    match = match * best_match[id][1][i]
                if (match >= config.MIN_READABLE_RESULT_VALUE):
                    stack[i] = id
                    weighting[i] = round(best_match[id][1][i],2)
            stacked_results.append([stack, weighting])
        for result in stacked_results:
            for i, id in enumerate(result[0]):
                if (id in confidence):
                    confidence[id]['count'] += 1
                    if (result[1][i] > 0.25):
                        confidence[id]['score'] += 1
        for x in range(0, ll):
            result_arr = [ ]
            for y in range(0, len(stacked_results)):
                weight_arr = [ '', '', 0, 0, 0 ]
                id = stacked_results[y][0][x]
                w = stacked_results[y][1][x]
                if (id != ''):
                    weight_arr[0] = id
                    if (x in weighted_results[id]['results']):
                        weight_arr[1] = id
                    weight_arr[2] = w
                    weight_arr[3] = confidence[id]['score']
                    weight_arr[4] = confidence[id]['count']
                result_arr.append(weight_arr)
            weighted = sorted(result_arr, key=lambda x: x[2], reverse=True)
            scored = sorted(result_arr, key=lambda x: x[3], reverse=True)
            counted = sorted(result_arr, key=lambda x: x[4],reverse=True)
            if (weighted[0][0] == scored[0][0] == counted[0][0]):
                # We are quite confident that we got the right match
                pre_results[x] = weighted[0][0]
            else:
                if (weighted[0][2] >= 0.1):
                    # We are not 100% confident but it seems to be ok
                    if (weighted[0][0] == counted[0][0]):
                        pre_results[x] = weighted[0][0]
                    elif (scored[0][0] == counted[0][0]):
                        pre_results[x] = scored[0][0]
                    else:
                        print ('Write me!!! Decision for position '+str(x) + ' is not clear')
                        print weighted[0]
                        print scored[0]
                        print counted[0]
        if (self.debug):
            print ('confidence: '+str(confidence))
        return pre_results

    def get_boosted_results(self, pre_results, word_pos):
        if (pre_results == None):
            return
        word_count_assumption = len(word_pos)
        word_count = { }
        fill_word = ''
        for word in pre_results:
            if (word != ''):
                if (fill_word == ''):
                    fill_word = word
                if (word not in word_count):
                    word_count[word] = 0
                word_count[word] += 1
        word_count = sorted(word_count.items(), key=operator.itemgetter(1), reverse=True)
        words_to_eliminate = [ ]
        for i, o in enumerate(word_count):
            word, _ = o
            if (i >= word_count_assumption):
                words_to_eliminate.append(word)
        for eliminate in words_to_eliminate:
            for i, word in enumerate(pre_results):
                if (word == eliminate):
                    pre_results[i] = ''
                    if (self.debug):
                        print ('get_boosted_results eliminates '+eliminate)
        for i, result in enumerate(pre_results):
            if (result == ''):
                pre_results[i] = fill_word
            if (result != ''):
                fill_word = result

        word_count = { }
        for word in pre_results:
             if (word != ''):
                 if (word not in word_count):
                     word_count[word] = 0
                 word_count[word] += 1
        for eliminate in word_count:
            if (word_count[eliminate] * 1.0 / self.dict_analysis[eliminate]['min_tokens'] < 0.4): # TODO: Make configurable
                for i, word in enumerate(pre_results):
                    if (eliminate == word):
                        if (i+1 < len(pre_results)):
                            pre_results[i] = pre_results[i+1]                            
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
                if (last in self.dict_analysis and (config.SOFT_IGNORE_MIN_MAX == True or count >= self.dict_analysis[last]['min_tokens'] and count <= self.dict_analysis[last]['max_tokens'])):
                    readable_results.append(last)
                elif (last != '' and self.debug):
                    print ('get_readable_results failed for '+ last +' cause '+str(self.dict_analysis[last]['min_tokens']) + ' < ' +str(count) + ' > '+str(self.dict_analysis[last]['max_tokens']))
                count = 1
                start = i
            last = result
        return readable_results

    def validate_results(self, boosted_results, word_tendency, data):
        if (boosted_results == None):
            return None
        ll = len(boosted_results)
        last = ''
        start = 0
        count = 0
        validated_results = [ '' ] * ll
        for i, word in enumerate(boosted_results):
            if (i == 0 or (word == last and i < ll-1)):
                count += 1
            else:
                if (i == ll-1):
                    count += 1
                if (count > 0):
                    if (self.debug):
                        print ('checking '+last + ' from ' + str(start) + ' - ' + str(count))
                    check = self.word_shape_check(last, start, count, word_tendency, data)
                    if (check == True):
                        for a in range(start, start+count):
                            validated_results[a] = last
                start = i
                count = 0
            last = word
        # check % of results
        empty_count = 0
        for validate in validated_results:
            if (validate == ''):
                empty_count += 1
        if (empty_count > 0):
            lv = len(validated_results)*1.0
            validated_percentage = ((lv-empty_count) / lv)
        else:
            validated_percentage = 1
        if (validated_percentage < config.RESULT_PERCENTAGE):
            if (self.debug):
                print ('validated_results failed because validated_percentage == '+str(validated_percentage) + ' -> ' + str(len(validated_results)) + ' / ' + str(empty_count))
            return [ '' ] * ll
        return validated_results

    def word_shaper(self, start, count, data):
        ll = len(data)
        word_shape = [ ]
        for x in range(start, start + count):
            if (x < ll):
                d = data[x]
                characteristic, meta = d
                if (characteristic != None):
                    for m in meta:
                        if ('token_peaks' in m):
                            word_shape.extend(m['token_peaks'])
        return word_shape

    def word_shape_check(self, word, start, count, word_tendency, data):
        if (word not in self.dict_analysis):
            return False
        word_shape = self.word_shaper(start, count, data)
        max_shape_similarity = 0
        max_shape_length_similarity = 0
        for shape in self.dict_analysis[word]['shape']:
            shape_similarity = self.util.approach_similarity(word_shape, shape)
            shape_length_similarity = self.util.approach_length_similarity(word_shape, shape)
            if (shape_similarity > max_shape_similarity):
                max_shape_similarity = shape_similarity
            if (shape_length_similarity > max_shape_length_similarity):
                max_shape_length_similarity = shape_length_similarity
        if (max_shape_similarity >= config.SHAPE_SIMILARITY and max_shape_length_similarity >= config.SHAPE_LENGTH_SIMILARITY):
            return True
        if (self.debug):
            print ('Word shape check failed for '+ word +' at pos '+str(start) + '. Max was :'+str(max_shape_similarity)+'/'+str(max_shape_length_similarity))
        return False
 
    def analyze_first_token(self, first_guess, data):
        first_token_weighting = [ ]
        for id in first_guess:
            analysis_object = self.dict_analysis[id]
            results = first_guess[id]['results']
            if (self.debug):
                print ('analyzing first token for ' + id + ' at potential position ' + str(results))
            for i, pos in enumerate(results):
                d = data[pos]
                characteristic, meta = d
                fft_similarity = 0
                fft_distance = 0
                if (characteristic != None):
                    count = 0
                    for dcharacteristic in analysis_object['first_token']:
                        cfft = characteristic['fft_max']
                        dfft = dcharacteristic['fft_max']
                        temp = self.util.approach_similarity(cfft, dfft)
                        if (temp > fft_similarity):
                            fft_similarity = temp
                        temp = self.util.approach_distance(cfft, dfft)
                        if (temp > fft_distance):
                            fft_distance = temp
                    first_token_weighting.append([id, pos, round(fft_similarity,2), round(fft_distance,2)])
        return first_token_weighting

    def weight_first_token(self, first_token_weighting, startpos):
        weighted_results = { }
        for arr in first_token_weighting:
            if (arr[0] not in weighted_results):
                weighted_results[arr[0]] = { 'results': [ ], 'lmin': self.dict_analysis[arr[0]]['min_tokens'], 'lmax': self.dict_analysis[arr[0]]['max_tokens'] }
            if (arr[3] >= config.MIN_DISTANCE):
                if (arr[1] + (self.dict_analysis[arr[0]]['min_tokens']/2) <= len(startpos)):
                    weighted_results[arr[0]]['results'].append(arr[1])
                else:
                    if (self.debug):
                        print ('weight_first_token: kicking '+arr[0]+ ' at pos '+str(arr[1])+' from results as length does not match = '+str(arr[1] + self.dict_analysis[arr[0]]['min_tokens']))
            else:
                if (self.debug):
                    print ('weight_first_token: kicking '+arr[0]+ ' at pos '+str(arr[1])+' from results as distance = '+str(arr[3]))
        return weighted_results

    def deep_scan(self, first_guess, data):
        deep_guess = [ ]
        for id in first_guess:
            results = first_guess[id]['results']
            lmax = first_guess[id]['lmax']
            lmin = first_guess[id]['lmin']
            for i, pos in enumerate(results):
                if (self.debug):
                    print ('searching for ' + id + ' between ' + str(pos) + ' and ' + str(pos+lmax))
                value = self.word_compare(id, pos, lmin, lmax, data)
                if (value != None):
                    deep_guess.append(value)
                else:
                    if (self.debug):
                        print (id + ' at ' + str(pos) + ' did not pass word_compare')
        return deep_guess

    def first_scan(self, pre_results, startpos, word_tendency, data):
        first_guess = { }
        for start in range(0, word_tendency['peaks']):
            for end in xrange(word_tendency['peaks'], 0, -1):
                for id in self.dict_analysis:
                    if (id not in first_guess):
                        p = end - start
                        if (p >= self.dict_analysis[id]['min_peaks'] and p <= self.dict_analysis[id]['max_peaks']):
                            first_guess[id] = { 'results': [], 'lmin': self.dict_analysis[id]['min_tokens'], 'lmax': self.dict_analysis[id]['max_tokens'] }
        if (not first_guess):
            if (self.debug):
                print ('first guess got no results ... now adding all dict entries!') # TODO: We need something better
            for id in self.dict_analysis:
                first_guess[id] = { 'results': [], 'lmin': self.dict_analysis[id]['min_tokens'], 'lmax': self.dict_analysis[id]['max_tokens'] }
        startwords = [ ]
        for i, words in enumerate(pre_results):
            # we add some more potential positions as words overlap quite a bit
            match = words[0]
            for x in range(config.SEARCH_POTENTIAL_POSITION_LEFT, config.SEARCH_POTENTIAL_POSITION_RIGHT, 1):
                matchr = match + x
                if (matchr >= 0 and matchr not in startwords and matchr < len(startpos)):
                    startwords.append(matchr)
        for id in first_guess:
            for i, startword in enumerate(startwords):
                if (self.fast_high_compare(id, startword, data, len(startpos)) > 0):
                    first_guess[id]['results'].append( startword )
        return first_guess

    def fast_high_compare(self, id, start, data, token_length):
        d = data[start]
        characteristic, meta = d
        if (characteristic != None):
            analysis_object = self.dict_analysis[id]
            fft_sum, fft_len = self.util.get_sum_len(characteristic['fft_max'])
            fft_sqr = self.util.sqr(characteristic['fft_max'])
            for cal_fft_arr in analysis_object['cal_fft']:
                for x in range(0,2): # TODO: Make configurable
                    if (x < len(cal_fft_arr)):
                         cal_fft = cal_fft_arr[x]
                         cal_fft_sum = cal_fft[0]
                         cal_fft_len = cal_fft[1]
                         cal_fft_sqr = cal_fft[2]
                         similarity_fft_sum = self.util.approach_fast_similarity(fft_sum, cal_fft_sum)
                         similarity_fft_sqr = self.util.approach_fast_similarity(fft_sqr, cal_fft_sqr)
                         similarity_fft = (similarity_fft_sum + similarity_fft_sum) / 2
                         if (similarity_fft >= config.FAST_HIGH_COMPARE_MARGINAL_VALUE and ((start + analysis_object['min_tokens'])/2) <= token_length): # TODO: Check if 1/2 is feasible
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
                else:
                    match_array.append([{ 'tendency_similarity': 0, 'fft_similarity': 0, 'fft_distance': 0, 'weighting': 0 }])
        points = self.calculate_points(id, start, match_array, lmin)
        return [id, start, points]

    def calculate_points(self, id, start, match_array, lmin):
        points = [ ]
        ll = len(match_array)
        if (ll < lmin):
            print ('warning: calculate_points for '+id+' failed at '+str(start)+' as ll < min failed: '+str(ll)+' < ' + str(lmin))
            return [ 0 ], [ 0 ]
        for i, arr in enumerate(match_array):
            fft_similarity_min, fft_similarity_max, fft_similarity_avg = self.get_similarity(arr, 'fft_similarity')
            tendency_similarity_min, tendency_similarity_max, tendency_similarity_avg = self.get_similarity(arr, 'tendency_similarity')
            distance_min, distance_max, distance_avg = self.get_similarity(arr, 'fft_distance')
            weighting = self.get_weighting(arr)
            point = fft_similarity_avg * config.FFT_SIMILARITY
            point += distance_avg * config.FFT_DISTANCE
            point += tendency_similarity_avg * config.TENDENCY_SIMILARITY
            if (point > 1):
                print ('warning: calculate_points for '+id+' at pos '+str(start)+' revealed a total point sum > 1:'+str(point))           
            points.append([round(point,2), weighting])
        return points

    def get_weighting(self, arr):
        weighting = 0
        counter = 0
        for s in arr:
            weighting += s['weighting']
            counter += 1.0
        if (counter == 0):
            return 0
        return weighting/counter

    def get_similarity(self, arr, field):
        similarity_max = 0
        similarity_min = 1
        similarity_avg = 0
        counter = 0
        for similarity in arr:
            v = similarity[field]
            similarity_avg += v
            if (v > similarity_max):
                similarity_max = v
            if (v < similarity_min):
                similarity_min = v
            counter += 1.0
        similarity_avg = similarity_avg / counter
        return similarity_min, similarity_max, similarity_avg

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
        for i, d in enumerate(data):
            characteristic, meta = d
            endpos.append(i)
            for m in meta:
                token = m['token']
                if (token != 'stop'):
                    if (token == 'token' or token == 'silence' or token == 'start analysis'):
                        posmapper.append(m['pos'])
        last = 0
        for x in range(0, len(endpos)):
            if (x < len(posmapper) and last < len(word_tendency['start_pos'])):  
                if (posmapper[x] >= word_tendency['start_pos'][last]):
                    startpos.append(x)
                    last += 1
                    if (last >= len(word_tendency['start_pos'])):
                        break
        wordpos = [ ]
        if (len(endpos) > 0 and len(startpos) > 0):
            for start in startpos:
                word = [ ]
                for end in endpos:
                    if (start <= end):
                        word.append(end)
                if (len(word) > 0 and word not in wordpos): # TODO: Eventually add max word length
                    wordpos.append(word)
        else:
            wordpos.append(endpos)
        if (self.debug):
            print ('wordpos : '+str(wordpos))
        
        cleanstartpos = [ ]
        remove = [ ]
        for i, d in enumerate(data):
            characteristic, meta = d
            if (characteristic == None):
                remove.append(i)
        for e in endpos:
            if (e not in remove):
                cleanstartpos.append(e)
        return wordpos, cleanstartpos

    def token_compare(self, id, pos, characteristic, match_array):
        similarity_array = [ ]
        for dict_entries in self.DICT['dict']:
            did = dict_entries['id']
            if (id == did and pos < len(dict_entries['characteristic'])):
                tendency = characteristic['tendency']
                fft_max = characteristic['fft_max']
                fft_freq = characteristic['fft_freq']
                dict_tendency = dict_entries['characteristic'][pos]['tendency']
                dict_fft_max = dict_entries['characteristic'][pos]['fft_max']
                dict_fft_freq = dict_entries['characteristic'][pos]['fft_freq']
                tendency_similarity = self.util.approach_similarity(
                 [fft_freq, tendency['len'], tendency['avg'], tendency['delta'], tendency['deg'] ],
                 [dict_fft_freq, dict_tendency['len'], dict_tendency['avg'],  dict_tendency['delta'], dict_tendency['deg']]
                )
                fft_similarity = self.util.approach_similarity(fft_max, dict_fft_max)
                fft_distance = self.util.approach_distance(fft_max, dict_fft_max)
                similarity_array.append({ 'tendency_similarity': tendency_similarity, 'fft_similarity': fft_similarity, 'fft_distance': fft_distance, 'weighting': dict_entries['characteristic'][pos]['weighting'] })
        match_array.append(similarity_array)
