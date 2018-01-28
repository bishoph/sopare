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

import logging

class log():

    def __init__(self, debug, error, cfg = None):
        if (error == True):
            logging.basicConfig(filename='error.log', filemode='a', loglevel='ERROR')
        else:
            logging.basicConfig()
        self.logger = logging.getLogger()
        self.logformat = '%(levelname)s: %(message)s'
        self.loglevel = 'ERROR'
        if (error == False and cfg != None and cfg.hasoption('misc', 'LOGLEVEL')):
            check = cfg.getoption('misc', 'LOGLEVEL')
            if (check != ''):
                self.loglevel = check
        if (error == False and debug == True):
            self.loglevel = 'DEBUG'
        self.logger.setLevel(self.loglevel)
        ch = logging.StreamHandler()
        ch.setFormatter(self.logformat)

    def getlog(self):
        return self.logger
