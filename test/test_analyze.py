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
import sopare.analyze as analyze

class test_analyze(unittest.TestCase):

    def __init__(self, debug, cfg):
        print ('analyze test preparation...')
        self.cfg = cfg
        self.util = util.util(debug, cfg.getfloatoption('characteristic', 'PEAK_FACTOR'))
        self.analyze = analyze.analyze(cfg)
        self.test_dict = self.create_test_dict()
        self.dict_analysis = self.analyze.prepare_test_analysis(self.test_dict)
        self.test_analyze_get_match()
        print ('analyze tests run successful.')

    def create_test_dict(self):
        test_dict = self.util.getDICT('test/test_dict.json')
        return test_dict

    def test_analyze_get_match(self):
        print ('testing analyze get_match...')
        # Normal conditions
        for t in range(1,4):
            test_framing, correct_object = self.create_test_framing(t)
            result = self.analyze.get_match(test_framing)
            print ('testing normal conditions (' + str(t) + ')' +str(result) + ' == ' + str(correct_object))
            self.assertSequenceEqual(result, correct_object, 'test_analyze_get_match('+str(t)+') failed!')

        # Testing leading empty results
        test_framing, correct_object = self.create_test_framing(t)
        test_framing.insert(0, '')
        self.cfg.setoption('compare', 'FILL_RESULT_PERCENTAGE', '0.1')
        result = self.analyze.get_match(test_framing)
        print ('testing leading space '+str(result) + ' == ' + str(correct_object))
        self.assertSequenceEqual(result, correct_object, 'test_analyze_get_match leading results failed!')

        # Testing ending empty results
        test_framing, correct_object = self.create_test_framing(t)
        test_framing.append('')
        result = self.analyze.get_match(test_framing)
        print ('testing ending space '+str(result) + ' == ' + str(correct_object))
        self.assertSequenceEqual(result, correct_object, 'test_analyze_get_match ending results failed!')

        # Testing correct order
        test_framing, correct_object = self.create_test_framing_order()
        result = self.analyze.get_match(test_framing)
        print ('testing correct order '+str(result) + ' == ' + str(correct_object))
        self.assertSequenceEqual(result, correct_object, 'test_analyze_get_match order results failed!')

        # Testing strict length
        self.cfg.setoption('compare' , 'STRICT_LENGTH_CHECK', 'True')
        #config.STRICT_LENGTH_UNDERMINING = 2
        test_framing, correct_object = self.create_test_framing_order_strict_length()
        result = self.analyze.get_match(test_framing)
        print ('testing strict length '+str(result) + ' == ' + str(correct_object))
        self.assertSequenceEqual(result, correct_object, 'test_analyze_get_match strict length results failed!')

        # Testing false leading results
        self.cfg.setoption('compare' , 'STRICT_LENGTH_CHECK', 'True')
        test_framing, correct_object = self.create_test_framing_false_leading_results()
        result = self.analyze.get_match(test_framing)
        print ('testing false leading results '+str(result) + ' == ' + str(correct_object))
        self.assertSequenceEqual(result, correct_object, 'test_analyze_get_match false leading results failed!')

    def create_test_framing(self, number):
        test_framing = [ ]
        correct_object = [ ]
        for id in self.dict_analysis:
            correct_object.append(id)
            for x in range(0, self.dict_analysis[id]['min_tokens']):
                test_framing.append(id)
            if (len(correct_object) == number):
                break
        return test_framing, correct_object

    def create_test_framing_order(self):
        test_framing = [ ]
        correct_object = [ ]
        for c in range(0,2):
            for id in self.dict_analysis:
                correct_object.append(id)
                for x in range(0, self.dict_analysis[id]['min_tokens']):
                    test_framing.append(id)
        return test_framing, correct_object

    def create_test_framing_order_strict_length(self):
        test_framing = [ ]
        correct_object = [ ]
        single_frames = [ ]
        for id in self.dict_analysis:
            correct_object.append(id)
            frame = [ ]
            for x in range(0, self.dict_analysis[id]['min_tokens']):
                frame.append(id)
            single_frames.append(frame)
        test_framing.extend(single_frames[0])
        test_framing.extend(single_frames[1])
        too_short = single_frames[0][0: len(single_frames[0]) - (self.cfg.getintoption('compare', 'STRICT_LENGTH_UNDERMINING') + 1)]
        test_framing.extend(too_short)
        test_framing.extend(single_frames[2])
        correct_object.insert(2, '')
        return test_framing, correct_object

    def create_test_framing_false_leading_results(self):
        test_framing = [ ]
        correct_object = [ ]
        temp = None
        for i, id in enumerate(self.dict_analysis):
            len = 1
            if (i % 2 == 0):
                len = self.dict_analysis[id]['min_tokens']
                correct_object.append(id)
                temp = id
            else:
                correct_object.append('')
            for x in range(0, len):
                test_framing.append(id)
        test_framing.insert(0, temp)
        correct_object.insert(0, '')
        return test_framing, correct_object
