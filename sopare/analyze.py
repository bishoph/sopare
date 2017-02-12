#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 - 2017 Martin Kauss (yo@bishoph.org)

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
        self.util = util.util(debug)
        self.learned_dict = self.util.getDICT()
        self.dict_analysis = self.util.compile_analysis(self.learned_dict)
        self.plugins = [ ]
        self.load_plugins()
        self.last_results = None

    def do_analysis(self, results, data, rawbuf):
        framing = self.framing(results, len(data))
        self.debug_info = '************************************************\n\n'
        if (self.debug):
            self.debug_info += ''.join([str(data), '\n\n'])
            self.debug_info += ''.join([str(results), '\n\n'])
        matches = self.deep_search(framing, data)
        readable_results = self.get_match(matches)
        if (self.debug):
            print (self.debug_info)
        if (readable_results != None):
            for p in self.plugins:
                p.run(readable_results, self.debug_info, rawbuf)

    def framing(self, results, data_length):
        framing = { }
        for id in results:
            framing[id] = [ ]
            for i, row in enumerate(results[id]):
                row = self.row_validation(row, id)
                row_result = sum(row[0:len(row)]) / self.dict_analysis[id]['min_tokens']
                if (row_result >= config.MARGINAL_VALUE):
                    framing[id].append(i)
        return framing

    def row_validation(self, row, id):
        if (row[0] == 0 or len(row) <= config.MIN_START_TOKENS):
            return [ 0 ] * len(row)
        return row

    def deep_search(self, framing, data):
        framing_match = [ ]
        match_results = [ '' ] * len(data)
        high_results = [ 0 ] * len(data)
        for id in framing:
            for startpos in framing[id]:
                xsim, xtsim, word_length = self.deep_inspection(id, startpos, data)
                framing_match.append([id, startpos, xsim, xtsim, word_length])
        for frame in framing_match:
            xpos = 0
            for x in range(frame[1], frame[1] + frame[4]):
                if (x < len(high_results) and frame[2] > high_results[x]):
                    high_results[x] = frame[2]
                    match_results[x] = frame[0]
                xpos += 1
        result_set = set(match_results)        
        self.debug_info += ''.join([str(framing), '\n'])
        self.debug_info += ''.join([str(framing_match), '\n'])
        self.debug_info += ''.join([str(match_results), '\n'])
        self.debug_info += ''.join([str(high_results), '\n'])
        check_length = 0
        for result in result_set:
            if (result != ''):
                check_length += self.dict_analysis[id]['max_tokens'] + 4 # TODO: Cross check and eventually make configurable
        if (check_length < len(match_results)):
            if (self.debug):
                print ('length check failed :'+str(check_length) + '/' + str(len(match_results)))
            return [ '' ] * len(data)
        return match_results

    def deep_inspection(self, id, startpos, data):
        if (startpos + (self.dict_analysis[id]['min_tokens']) > len(data)):
            if (self.debug):
                print ('deep_inspection failed for '+id+'/'+str(startpos))
            return 0, 0, 0
        high_sim = 0
        high_token_sim = [ ]
        bias = [ ]
        word_length = 0
        for dict_entries in self.learned_dict['dict']:
            if (id == dict_entries['id']):
                dict_characteristic = dict_entries['characteristic']
                word_sim = 0
                bias_tokens = [ ]
                token_sim = [ 0 ] * len(dict_characteristic)
                c = 0.0
                for i, dcharacteristic in enumerate(dict_characteristic):
                    bias_obj = { }
                    currentpos = startpos + i
                    if (currentpos < len(data)):
                        do = data[currentpos]
                        characteristic, _ = do
                        sim = 0
                        ll = len(characteristic['peaks'])
                        bias_obj['i'] = i
                        if (ll > 0):
                            sim_peaks = self.util.similarity(characteristic['norm'], dcharacteristic['norm']) * config.SIMILARITY_PEAKS
                            sim_token_peaks = self.util.similarity(characteristic['token_peaks'], dcharacteristic['token_peaks']) * config.SIMILARITY_HEIGHT
                            sim_df = self.util.single_similarity(characteristic['df'], dcharacteristic['df']) * config.SIMILARITY_DOMINANT_FREQUENCY
                            sim = sim_peaks + sim_token_peaks + sim_df
                            if (config.BIAS > 0):
                                if (characteristic['df'] in self.dict_analysis[id]['df'][i]):
                                    bias_obj['df'] = 1
                                else:
                                    bias_obj['df'] = 0
                                xmin = min(characteristic['peaks'])
                                xmax = max(characteristic['peaks'])
                                if (xmin >= self.dict_analysis[id]['minp'][i] and xmax <= self.dict_analysis[id]['maxp'][i]):
                                    sim = sim + 0.1
                                    bias_obj['sr'] = 1
                                else:
                                    bias_obj['sr'] = 0
                                if (ll >= self.dict_analysis[id]['mincp'][i] and ll <= self.dict_analysis[id]['maxcp'][i]):
                                    sim = sim + 0.1
                                    bias_obj['sl'] = 1
                                else:
                                    bias_obj['sl'] = 0
                        token_sim[i] = sim    
                        word_sim += sim
                        bias_tokens.append(bias_obj)
                    c += 1
                word_sim = word_sim / c
                bias.append(bias_tokens)
                if (word_sim > 1):
                    word_sim = 1
                if (word_sim > high_sim and word_sim > config.MIN_CROSS_SIMILARITY):
                    bc = self.calculate_bias(bias)
                    if (bc >= config.BIAS):
                        high_sim = word_sim
                        word_length = int(c)
                        high_token_sim.append(token_sim)
        consolidated_high_token_sim = [ ]
        for hts in high_token_sim:
            for i, ts in enumerate(hts):
                if (i == len(consolidated_high_token_sim)):
                    consolidated_high_token_sim.append(ts)
                elif (ts > consolidated_high_token_sim[i]):
                    consolidated_high_token_sim[i] = ts
        if (len(consolidated_high_token_sim) > 0):
            consolidated_high_sim = sum(consolidated_high_token_sim) / len(consolidated_high_token_sim)
            return consolidated_high_sim, consolidated_high_token_sim, word_length
        else:
            return high_sim, high_token_sim, word_length

    @staticmethod
    def calculate_bias(bias):
        bc = 0
        cc = 0
        for b in bias:
            for e in b:
                if (len(e) == 4):
                    bc += e['df'] + e['sr'] + e['sl']
                    cc += 3.0
        if (cc > 0):
            return bc/cc
        return 0

    def get_match(self, framing):
        match_results = [ ]
        counter = 0
        last = ''
        for check in framing:
            if (check == last):
                counter += 1
            else:
                if (last != ''):
                    if (counter >= self.dict_analysis[last]['min_tokens']-1 and counter <= self.dict_analysis[last]['max_tokens']+1): # TODO: x-check
                        match_results.append(last)
                    elif (self.debug):
                        print ('length check failed for :'+last+' from results. ' + str(self.dict_analysis[last]['min_tokens']-1) + ' ' + str(counter) + ' ' + str(self.dict_analysis[last]['max_tokens']+1))
                counter = 1
            last = check
        if (last != ''):
            if (counter >= self.dict_analysis[last]['min_tokens']-1 and counter <= self.dict_analysis[last]['max_tokens']+1): # TODO: x-check
                match_results.append(last)
            elif  (self.debug):
                print ('length check failed for :'+last+' from results. ' + str(self.dict_analysis[last]['min_tokens']-1) + ' ' + str(counter) + ' ' + str(self.dict_analysis[last]['max_tokens']+1))
        return match_results

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

    def reset(self):
        self.last_results = None
