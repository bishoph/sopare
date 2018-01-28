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

import time
import logging

class short_term_memory():

    def __init__(self, cfg):
        self.cfg = cfg
        self.debug = self.cfg.getbool('cmdlopt', 'debug')
        self.last_debug_info = ''
        self.last_results = [ ]
        self.last_time = 0

    def get_stm_results(self, results):
        stm_results = self.last_results[:]
        stm_results.extend(results)
        return stm_results

    def get_stm_debug_info(self, debug_info):
        return self.last_debug_info + debug_info

    def get_results(self, results, debug_info):
        if (results == None or len(results) == 0):
            return results, debug_info
        if (time.time() < self.last_time):
            logging.debug('stm input: ' + str(results) + ' '  + str(self.last_results))
            results = self.get_stm_results(results)
            debug_info = self.get_stm_debug_info(debug_info)
            logging.debug('stm mnodification: ' + str(results))
        self.last_results = results
        self.last_debug_info = debug_info
        self.last_time = time.time() + self.cfg.getfloatoption('compare', 'STM_RETENTION')
        return results, debug_info
