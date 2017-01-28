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

import config

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
        self.area(characteristics[ll], ll)

    def area(self, characteristic_object, ll):
        characteristic, _ = characteristic_object
        for dict_entries in self.learned_dictionary['dict']:
            id = dict_entries['id']
            dict_characteristic = dict_entries['characteristic']
            for i, dcharacteristic in enumerate(dict_characteristic):
                if (i > config.COMPARE_START_TOKENS):
                    break
                fft_sim = self.util.similarity(characteristic['peaks'], dcharacteristic['peaks'])
                fft_sim += self.util.similarity(characteristic['token_peaks'], dcharacteristic['token_peaks'])
                fft_sim += self.util.single_similarity(characteristic['df'], dcharacteristic['df'])
                fft_sim = round(fft_sim / 3.0, 2)
                if (fft_sim > config.MARGINAL_VALUE):
                    self.results[id].append([ll, i, fft_sim])
