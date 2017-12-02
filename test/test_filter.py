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

import unittest
import sopare.util as util
import sopare.config as config
import sopare.filter as filter
import sopare.log as log

class test_filter(unittest.TestCase):

    def __init__(self, debug, cfg):
        print ('filter test preparation...')
        self.util = util.util(debug, cfg.getfloatoption('characteristic', 'PEAK_FACTOR'))
        cfg.setoption('stream', 'CHUNKS', '10')
        self.filter = filter.filtering(cfg)
        self.CHUNKS = 10
        self.test_filter_n_shift()
        print ('filter tests run successful.')
        self.filter.stop()

    def test_filter_n_shift(self):
        print ('testing filter n_shift...')
        data_object_array = [ v for v in range(0, 40) ]
        for x in xrange(0, len(data_object_array), self.CHUNKS):
            data_object = data_object_array[x:x+self.CHUNKS]
            self.filter.n_shift(data_object)
            correct_object = [ ]
            if (x == 0):
                self.filter.first = False
            else:
                correct_object = data_object_array[x-self.CHUNKS/2:x+self.CHUNKS/2]
                print ('testing n_shift '+str(self.filter.data_shift) + ' == ' + str(correct_object))
                self.assertSequenceEqual(self.filter.data_shift, correct_object, 'test_filter_n_shift 0 failed!')
