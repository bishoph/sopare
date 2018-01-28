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

import ConfigParser

class config():

    def __init__(self, config_file = 'config/default.ini'):
        self.config = ConfigParser.ConfigParser(allow_no_value=True)
        self.config.read(config_file)
        self.logger = None

    def getoption(self, section, option):
        return self.config.get(section, option)

    def getfloatoption(self, section, option):
        return self.config.getfloat(section, option)

    def getintoption(self, section, option):
        return self.config.getint(section, option)

    def getbool(self, section, option):
        return self.config.getboolean(section, option)

    def addsection(self, section):
        self.config.add_section(section)

    def setoption(self, section, id, option):
        self.config.set(section, id, option)

    def hasoption(self, section, option):
        return self.config.has_option(section, option)

    def addlogger(self, logger):
        self.logger = logger

    def getlogger(self):
        return self.logger

    def showconfig(self):
        print ('current config:')
        for section in self.config.sections():
            print (str(section))
            for option in self.config.options(section):
                print (' ' + str(option) + ' = ' + str(self.getoption(section, option)))
