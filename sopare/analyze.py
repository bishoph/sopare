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

from operator import itemgetter
import characteristics
import config
import stm
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
        self.stm = stm.short_term_memory(debug)
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
        readable_results = self.stm.get_results(readable_results)
        if (self.debug):
            print (self.debug_info)
        if (readable_results != None):
            for p in self.plugins:
                p.run(readable_results, self.debug_info, rawbuf)

    def framing(self, results, data_length):
        framing = { }
        arr = [ ]
        for id in results:
            framing[id] = [ ]
            for i, row in enumerate(results[id]):
                row = self.row_validation(row, id)
                row_result = sum(row[0:len(row)]) / self.dict_analysis[id]['min_tokens']
                if (row_result >= config.MARGINAL_VALUE):
                    arr.append([row_result, i, id])
        sorted_arr = sorted(arr, key=itemgetter(0), reverse = True)
        for el in sorted_arr:
            if (el[1] not in framing[el[2]] and (config.MAX_WORD_START_RESULTS == 0 or len(framing[el[2]]) < config.MAX_WORD_START_RESULTS)):
                framing[el[2]].append(el[1])
        return framing

    def row_validation(self, row, id):
        if (row[0] == 0 or len(row) <= config.MIN_START_TOKENS):
            return [ 0 ] * len(row)
        return row

    def deep_search(self, framing, data):
        framing_match = [ ]
        match_results = [ '' ] * len(data)
        for id in framing:
            for startpos in framing[id]:
                word_sim = self.deep_inspection(id, startpos, data)
                if (len(word_sim) > 0):
                    framing_match.append(word_sim)
        self.debug_info += str(framing_match).join(['framing_match: ', '\n\n'])
        best_match = [ ]
        for match in framing_match:
            sorted_framing_match = sorted(match, key=lambda x: (x[1] + x[2], -x[0]))
            nobm = 1
            if (hasattr(config, 'NUMBER_OF_BEST_MATCHES') and config.NUMBER_OF_BEST_MATCHES > 0):
                nobm = config.NUMBER_OF_BEST_MATCHES
            for x in range(0, nobm):
               if (x < len(sorted_framing_match)):
                   best_match.append(sorted_framing_match[x])
        sorted_best_match = sorted(best_match, key=lambda x: (x[1] +  x[2], -x[0]))
        self.debug_info += str(sorted_best_match).join(['sorted_best_match: ', '\n\n'])
        for i, best in enumerate(sorted_best_match):
            if (best[0] >= config.MIN_CROSS_SIMILARITY and best[1] <= config.MIN_LEFT_DISTANCE and best[2] <= config.MIN_RIGHT_DISTANCE):
                for x in range(best[3], best[3] + best[4]):
                    if (match_results[x] == ''):
                        match_results[x] = best[5]
            if (config.MAX_TOP_RESULTS > 0 and i > config.MAX_TOP_RESULTS):
                break
        self.debug_info += str(match_results).join(['match_results: ', '\n\n'])
        return match_results

    def deep_inspection(self, id, startpos, data):
        word_sim = [ ]
        for dict_entries in self.learned_dict['dict']:
            if (id == dict_entries['id']):
                dict_characteristic = dict_entries['characteristic']
                token_sim = [ 0, 0, 0, startpos, 0, id ]
                c = 0
                for i, dcharacteristic in enumerate(dict_characteristic):
                    if (startpos + i < len(data)):
                        do = data[startpos + i]
                        characteristic, _ = do
                        sim_norm = self.util.similarity(characteristic['norm'], dcharacteristic['norm']) * config.SIMILARITY_NORM
                        sim_token_peaks = self.util.similarity(characteristic['token_peaks'], dcharacteristic['token_peaks']) * config.SIMILARITY_HEIGHT
                        sim_df = self.util.single_similarity(characteristic['df'], dcharacteristic['df']) * config.SIMILARITY_DOMINANT_FREQUENCY
                        sim = sim_norm + sim_token_peaks + sim_df
                        sl, sr = self.util.manhatten_distance(characteristic['norm'], dcharacteristic['norm'])
                        token_sim[0] += sim
                        token_sim[1] += sl
                        token_sim[2] += sr
                        c += 1.0
                if (c > 0):
                    token_sim[0] = token_sim[0] / c
                    token_sim[1] = token_sim[1] / c
                    token_sim[2] = token_sim[2] / c
                    token_sim[4] = int(c)
                if ((config.STRICT_LENGTH_CHECK == False and c > 1 ) or c >= self.dict_analysis[id]['min_tokens'] - config.STRICT_LENGTH_UNDERMINING):
                    word_sim.append(token_sim)
        return word_sim

    def get_match(self, framing):
        match_results = [ ]
        s = 0
        for x in range(0, len(framing)):
            if (x > 0 and framing[x] != framing[x-1]):
                match_results = self.validate_match_result(framing[s:x], s, x, match_results)
                s = x
                if (x == len(framing)-1):
                    match_results = self.validate_match_result(framing[s:], s, x, match_results)
            elif (x == len(framing)-1):
                match_results = self.validate_match_result(framing[s:], s, x, match_results)
        if (framing.count('') > len(framing) * config.FILL_RESULT_PERCENTAGE):
            if (self.debug):
                self.debug_info += 'Results contain too many empty tokens. ' + str(framing.count('')) + ' / ' + str(len(framing)) + ' Eliminating results'
            return [ ] * len(match_results)
        return match_results

    def validate_match_result(self, result, start, end, match_results):
        if (len(result) == 0 or result[0] == '' or end-start < 2):
            return match_results
        if (config.STRICT_LENGTH_CHECK == True and (len(result) < self.dict_analysis[result[0]]['min_tokens'] - config.STRICT_LENGTH_UNDERMINING or len(result) > self.dict_analysis[result[0]]['max_tokens'])):
            if (self.debug):
                self.debug_info += 'STRICT_LENGTH_CHECK failed for '+result[0] + ': ' + str(self.dict_analysis[result[0]]['min_tokens']) + ' > ' + str(len(result)) + ' < ' + str(self.dict_analysis[result[0]]['max_tokens']) + '\n'
            return match_results
        match_results.append(result[0])
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
