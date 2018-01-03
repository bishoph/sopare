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

import pyaudio
import logging

class audio_factory():

    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = self.cfg.getlogger().getlog()
        self.logger = logging.getLogger(__name__)
        self.stream = None
        self.pa = pyaudio.PyAudio()
        self.debug_once = False

    def open(self, sample_rate, input_format=pyaudio.paInt16):
        if (self.debug_once == False):
            self.logger.debug('#### Default input device info #####')
            for k, v in self.pa.get_default_input_device_info().iteritems():
                self.logger.debug(str(k) + ': ' + str(v))
            self.debug_once = True
        try:
            self.stream = self.pa.open(format = input_format,
                channels = 1, # mono
                rate=sample_rate,
                input=True,
                output=False,
                frames_per_buffer = self.cfg.getintoption('stream', 'CHUNK'))
        except IOError as e:
            self.logger.error("Error: " + str(e))
            return None
        return self.stream

    def close(self):
        if (self.stream != None):
            try:
                self.stream.stop_stream()
                self.stream.close()
            except IOError as e:
                self.logger.error("Error: " + str(e))

    def terminate(self):
        self.pa.terminate()
