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

class compare():

    def __init__(self, debug, util):
        self.debug = debug
        self.util = util
        self.learned_dictionary = self.util.getDICT()
        self.dict_analysis = self.util.compile_analysis(self.learned_dictionary)
        self.results = { }

    def reset(self):
        self.results = { }

    def get_results(self):
        return self.results

    def word(self, characteristics):
        ll = len(characteristics)-1
        if (ll == 0):
            self.results = { }
            for id in self.dict_analysis:
                self.results[id] = [ ]
        self.create_structure()
        self.fill_structure(characteristics[ll])

    def create_structure(self):
        for id in self.dict_analysis:
            self.results[id].append([ ])
            for x in range(0, len(self.results[id])):
                self.results[id][x].append(0)

    def fill_structure(self, characteristic_object):
        characteristic, meta = characteristic_object
        for dict_entries in self.learned_dictionary['dict']:
            id = dict_entries['id']
            for x in range(0, len(self.results[id])):
                dict_c_pos = len(self.results[id][x])-1
                if (dict_c_pos < len(dict_entries['characteristic'])):
                    dcharacteristic = dict_entries['characteristic'][dict_c_pos]
                    fc_sim = self.util.single_similarity(characteristic['fc'], dcharacteristic['fc'])
                    dfm_sim = self.util.single_similarity(characteristic['dfm'], dcharacteristic['dfm'])
                    volume_sim = 0
                    if (len(meta) > 0 and 'volume' in meta[0]):
                        volume_sim = self.util.single_similarity(meta[0]['volume'], dcharacteristic['volume'])
                    fast_sim = (fc_sim + dfm_sim + volume_sim) / 3.0
                    if (fast_sim > self.results[id][x][dict_c_pos]):
                        self.results[id][x][dict_c_pos] = fast_sim
                    if ('shift' in characteristic):
                        shift = characteristic['shift']
                        fc_sim = self.util.single_similarity(shift['fc'], dcharacteristic['fc'])
                        dfm_sim = self.util.single_similarity(shift['dfm'], dcharacteristic['dfm'])
                        fast_sim = (fc_sim + dfm_sim) / 2.0
                        if (fast_sim > self.results[id][x][dict_c_pos]):
                            self.results[id][x][dict_c_pos] = fast_sim

