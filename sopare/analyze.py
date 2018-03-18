#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 - 2018 Martin Kauss (yo@bishoph.org)

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
import sopare.characteristics
import sopare.stm
import sopare.path
import sopare.util
import logging
import imp
import os

class analyze():

    def __init__(self, cfg):
        self.cfg = cfg
        self.debug = self.cfg.getbool('cmdlopt', 'debug')
        self.util = sopare.util.util(self.debug, self.cfg.getfloatoption('characteristic', 'PEAK_FACTOR'))
        self.learned_dict = self.util.getDICT()
        self.dict_analysis = self.util.compile_analysis(self.learned_dict)
        self.stm = sopare.stm.short_term_memory(self.cfg)
        self.logger = self.cfg.getlogger().getlog()
        self.logger = logging.getLogger(__name__)
        self.plugins = [ ]
        self.load_plugins()
        self.last_results = None

    def prepare_test_analysis(self, test_dict):
        self.learned_dict = test_dict
        self.dict_analysis = self.util.compile_analysis(self.learned_dict)
        return self.dict_analysis

    def do_analysis(self, results, data, rawbuf):
        framing = self.framing(results, len(data))
        self.debug_info = '************************************************\n\n'
        if (self.debug):
            self.debug_info += ''.join([str(data), '\n\n'])
            self.debug_info += ''.join([str(results), '\n\n'])
        matches = self.deep_search(framing, data)
        readable_results = self.get_match(matches)
        readable_results, self.debug_info = self.stm.get_results(readable_results, self.debug_info)
        self.logger.debug(self.debug_info)
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
                if (row_result >= self.cfg.getfloatoption('compare', 'MARGINAL_VALUE')):
                    arr.append([row_result, i, id])
                else:
                    self.logger.debug('removing '+id + ' from potential start position '+str(i) + ' bc MARGINAL_VALUE > ' +str(row_result))
        sorted_arr = sorted(arr, key=itemgetter(0), reverse = True)
        for el in sorted_arr:
            if (el[1] not in framing[el[2]] and (self.cfg.getintoption('compare', 'MAX_WORD_START_RESULTS') == 0 or len(framing[el[2]]) < self.cfg.getintoption('compare', 'MAX_WORD_START_RESULTS'))):
                framing[el[2]].append(el[1])
        return framing

    def row_validation(self, row, id):
        if (row[0] == 0 or len(row) <= self.cfg.getintoption('compare', 'MIN_START_TOKENS')):
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
            if (self.cfg.hasoption('compare', 'NUMBER_OF_BEST_MATCHES') and self.cfg.getintoption('compare', 'NUMBER_OF_BEST_MATCHES') > 0):
                nobm = self.cfg.getintoption('compare', 'NUMBER_OF_BEST_MATCHES')
            for x in range(0, nobm):
               if (x < len(sorted_framing_match)):
                   best_match.append(sorted_framing_match[x])
        sorted_best_match = sorted(best_match, key=lambda x: (x[1] +  x[2], -x[0]))
        self.debug_info += str(sorted_best_match).join(['sorted_best_match: ', '\n\n'])
        for i, best in enumerate(sorted_best_match):
            if (best[0] >= self.cfg.getfloatoption('compare', 'MIN_CROSS_SIMILARITY') and best[1] <= self.cfg.getfloatoption('compare', 'MIN_LEFT_DISTANCE') and best[2] <= self.cfg.getfloatoption('compare', 'MIN_RIGHT_DISTANCE')):
                for x in range(best[3], best[3] + best[4]):
                    if (match_results[x] == ''):
                        match_results[x] = best[5]
            if (self.cfg.getintoption('compare', 'MAX_TOP_RESULTS') > 0 and i > self.cfg.getintoption('compare', 'MAX_TOP_RESULTS')):
                break
        self.debug_info += str(match_results).join(['match_results: ', '\n\n'])
        return match_results

    def token_sim(self, characteristic, dcharacteristic):
        sim_norm = self.util.similarity(characteristic['norm'], dcharacteristic['norm']) * self.cfg.getfloatoption('compare', 'SIMILARITY_NORM')
        sim_token_peaks = self.util.similarity(characteristic['token_peaks'], dcharacteristic['token_peaks']) * self.cfg.getfloatoption('compare', 'SIMILARITY_HEIGHT')
        sim_df = self.util.single_similarity(characteristic['df'], dcharacteristic['df']) * self.cfg.getfloatoption('compare', 'SIMILARITY_DOMINANT_FREQUENCY')
        sim_zcr = self.util.single_similarity(characteristic['zcr'], dcharacteristic['zcr']) * self.cfg.getfloatoption('compare', 'SIMILARITY_ZERO_CROSSING_RATE')

        sim = sim_norm + sim_token_peaks + sim_df + sim_zcr
        sl, sr = self.util.manhatten_distance(characteristic['norm'], dcharacteristic['norm'])
        return sim, sl, sr

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
                        sim, sl, sr = self.token_sim(characteristic, dcharacteristic)
                        if ('shift' in characteristic):
                            ssim, ssl, ssr = self.token_sim(characteristic['shift'], dcharacteristic)
                            if (ssim > sim):
                                ssim = sim
                            if  (ssr < sr):
                                sr = ssr
                            if (ssl < sl):
                                sl = ssl
                        token_sim[0] += sim
                        token_sim[1] += sl
                        token_sim[2] += sr
                        c += 1.0
                if (c > 0):
                    token_sim[0] = token_sim[0] / c
                    if (token_sim[0] > 1.0 and c >= self.cfg.getintoption('compare', 'MIN_START_TOKENS') and c >= self.dict_analysis[id]['min_tokens']):
                        self.logger.warning('Your calculation basis seems to be wrong as we get results > 1.0!')
                    token_sim[1] = token_sim[1] / c
                    token_sim[2] = token_sim[2] / c
                    token_sim[4] = int(c)
                if ((self.cfg.getbool('compare', 'STRICT_LENGTH_CHECK') == False and c >= self.cfg.getintoption('compare', 'MIN_START_TOKENS')) or c >= self.dict_analysis[id]['min_tokens'] - self.cfg.getintoption('compare', 'STRICT_LENGTH_UNDERMINING')):
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
        if (framing.count('') > len(framing) * self.cfg.getfloatoption('compare', 'FILL_RESULT_PERCENTAGE')):
            if (self.debug):
                self.debug_info += 'Results contain too many empty tokens. ' + str(framing.count('')) + ' / ' + str(len(framing)) + ' Eliminating results'
            return [ ] * len(match_results)
        return match_results

    def validate_match_result(self, result, start, end, match_results):
        if (len(result) == 0 or result[0] == ''):
            return match_results
        if (self.cfg.getbool('compare', 'STRICT_LENGTH_CHECK') == True and (len(result) < self.dict_analysis[result[0]]['min_tokens'] - self.cfg.getintoption('compare', 'STRICT_LENGTH_UNDERMINING') or len(result) > self.dict_analysis[result[0]]['max_tokens'])):
            if (self.debug):
                self.debug_info += 'STRICT_LENGTH_CHECK failed for '+result[0] + ': ' + str(self.dict_analysis[result[0]]['min_tokens']) + ' > ' + str(len(result)) + ' < ' + str(self.dict_analysis[result[0]]['max_tokens']) + '\n'
            match_results.append('')
            return match_results
        match_results.append(result[0])
        return match_results

    def load_plugins(self):
        self.logger.info('checking for plugins...')
        pluginsfound = os.listdir(sopare.path.__plugindestination__)
        for plugin in pluginsfound:
            try:
                pluginpath = os.path.join(sopare.path.__plugindestination__, plugin)
                self.logger.debug('loading and initialzing '+pluginpath)
                f, filename, description = imp.find_module('__init__', [pluginpath])
                self.plugins.append(imp.load_module(plugin, f, filename, description))
            except ImportError, err:
                self.logger.error('ImportError: %s', err)

    def reset(self):
        self.last_results = None
