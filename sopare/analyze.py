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
        self.util = util.util(debug)
        self.learned_dict = self.util.getDICT()
        self.dict_analysis = self.util.compile_analysis(self.learned_dict)
        self.plugins = [ ]
        self.load_plugins()
        self.last_results = None

    def do_analysis(self, results, data, rawbuf):
        self.debug_info = str(data)+'\n\n'
        self.debug_info = str(results)+'\n\n'
        framing = self.framing(results)
        matches = self.deep_search(framing, data)
        readable_results = self.get_match(matches)
        if (self.debug):
            print (self.debug_info)
        if (readable_results != None):
            for p in self.plugins:
                p.run(readable_results, self.debug_info, rawbuf)

    @staticmethod
    def framing(results):
        framing = { }
        for id in results:
            sorted_results = sorted(results[id], key=lambda x: x[1])
            framing[id] = [ ]
            for result in sorted_results:
                if (result[0] not in framing[id]):
                    framing[id].append(result[0])
        return framing

    def deep_search(self, framing, data):
        framing_match = [ ]
        match_results = [ '' ] * len(data)
        high_results = [ 0 ] * len(data)
        for id in framing:
            for startpos in framing[id]:
                xsim, word_length = self.deep_inspection(id, startpos, data)
                framing_match.append([id, startpos, xsim, word_length])
        for frame in framing_match:
            for x in range(frame[1], frame[1] + frame[3]):
                if (x < len(high_results) and frame[2] > high_results[x]):
                    high_results[x] = frame[2]
                    match_results[x] = frame[0]
        empty_results = 0
        for result in match_results:
            if (result == ''):
                empty_results += 1
        if (empty_results > 0):
            empty_percentage = empty_results / float(len(match_results))
            if (empty_percentage < config.MIN_RESULT_PERCENTAGE):
                if (self.debug):
                    self.debug_info += ('empty_percentage too low : '+str(empty_percentage))
                return [ '' ] * len(data)
        self.debug_info += str(framing) + '\n'
        self.debug_info += str(framing_match) + '\n'
        self.debug_info += str(match_results) + '\n'
        self.debug_info += str(high_results) + '\n' 
        return match_results

    def deep_inspection(self, id, startpos, data):
        if (startpos + (self.dict_analysis[id]['min_tokens']/2) > len(data)):
            return 0, 0
        high_sim = 0
        word_length = 0
        for dict_entries in self.learned_dict['dict']:
            if (id == dict_entries['id']):
                dict_characteristic = dict_entries['characteristic']
                word_sim = 0
                c = 0.0
                for i, dcharacteristic in enumerate(dict_characteristic):
                    currentpos = startpos + i
                    if (currentpos < len(data)):
                        do = data[currentpos]
                        characteristic, _ = do
                        sim_peaks = self.util.similarity(characteristic['peaks'], dcharacteristic['peaks']) * 0.3
                        sim_token_peaks = self.util.similarity(characteristic['token_peaks'], dcharacteristic['token_peaks']) * 0.3
                        sim_df = self.util.single_similarity(characteristic['df'], dcharacteristic['df']) * 0.4
                        sim = sim_peaks + sim_token_peaks + sim_df
                        word_sim += sim
                    c += 1
                word_sim = word_sim / c
                if (word_sim > high_sim and word_sim > config.MIN_CROSS_SIMILARITY):
                    high_sim = word_sim
                    # TODO: Check for better options
                    word_length = self.dict_analysis[id]['min_tokens'] / 2
        return high_sim, word_length

    def get_match(self, framing):
        print framing
        match_results = [ ]
        removes = [ ]
        for result in framing:
            if (result != '' and result not in match_results):
                match_results.append(result)
        for result in match_results:
            if (framing.count(result) < (self.dict_analysis[result]['min_tokens'] / 2)-1 or framing.count(result) > self.dict_analysis[result]['max_tokens']):
                removes.append(result)
        for remove in removes:
            #if (self.debug):
            print ('removing ' + remove + ' due to min_length check :' + str(framing.count(remove)) +  ' / ' + str((self.dict_analysis[remove]['min_tokens'] / 2)-1))
            match_results.remove(remove)
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
