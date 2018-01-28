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

import multiprocessing
import logging
import uuid
import sopare.util
import sopare.visual
import sopare.analyze
import sopare.characteristics
import sopare.comparator

class worker(multiprocessing.Process):

    def __init__(self, cfg, queue):
        multiprocessing.Process.__init__(self, name="worker for filtered data")
        self.cfg = cfg
        self.queue = queue
        self.visual = sopare.visual.visual()
        self.util = sopare.util.util(self.cfg.getbool('cmdlopt', 'debug'), self.cfg.getfloatoption('characteristic', 'PEAK_FACTOR'))
        self.logger = self.cfg.getlogger().getlog()
        self.logger = logging.getLogger(__name__)
        self.analyze = sopare.analyze.analyze(self.cfg)
        self.compare = sopare.comparator.compare(self.cfg.getbool('cmdlopt', 'debug'), self.util)
        self.running = True
        self.counter = 0
        self.plot_counter = 0
        self.reset_counter = 0
        self.rawbuf = [ ]
        self.rawfft = [ ]
        self.raw = [ ]
        self.fft = [ ]
        self.word_tendency = None
        self.character = [ ]
        self.raw_character = [ ]
        self.uid = str(uuid.uuid4())
        self.start()

    def reset(self):
        self.counter = 0
        if (self.cfg.getbool('cmdlopt', 'wave') == True and len(self.rawbuf) > 0):
            self.save_wave_buf()
        self.rawbuf = [ ]
        self.raw = [ ]
        self.fft = [ ]
        self.word_tendency = None
        self.character = [ ]
        self.raw_character = [ ]
        self.uid = str(uuid.uuid4())
        self.analyze.reset()
        self.reset_counter += 1
        self.compare.reset()

    def save_wave_buf(self):
        self.util.savefilteredwave('filtered_results'+str(self.reset_counter), self.rawbuf)

    def remove_silence(self, m):
        silence = ((self.cfg.getintoption('stream', 'LONG_SILENCE') * self.cfg.getintoption('stream', 'CHUNK')) / 4096) - 4 # TODO: Find auto value or make configurable
        if (silence < 0):
            silence = 0
        for x in range(len(self.character) - 1, len(self.character) - silence, -1):
            if (x <= len(self.character)-1 and x > 0):
                del self.character[x]
        if (len(self.raw_character) > 0):
            for x in range(len(self.raw_character) - 1, len(self.raw_character) - silence , -1):
                del self.raw_character[x]


    def run(self):
        self.logger.info("worker queue runner started")
        while self.running:
            obj = self.queue.get()
            if (obj['action'] == 'data'):
                raw_token = obj['token']
                if (self.cfg.getbool('cmdlopt', 'wave') == True or True): # TODO: "or True" is just temporary for testing. Must be removed later on!
                    self.rawbuf.extend(raw_token)
                fft = obj['fft']
                if (self.cfg.getbool('cmdlopt', 'plot') == True):
                    self.rawfft.extend(fft)
                meta = obj['meta']
                norm = obj['norm']
                characteristic = obj['characteristic']
                self.character.append((characteristic, meta))
                self.compare.word(self.character)
                if (self.cfg.getoption('cmdlopt', 'dict') != None):
                    self.raw_character.append({ 'fft': fft, 'norm': norm, 'meta': meta })
                if (characteristic != None):
                    self.logger.debug('characteristic = ' + str(self.counter) + ' ' + str(characteristic))
                    self.logger.debug('meta = '+str(meta))
                    if (self.cfg.getbool('cmdlopt', 'wave') == True):
                        self.util.savefilteredwave('token'+str(self.counter)+self.uid, raw_token)
                    if (self.cfg.getbool('cmdlopt', 'plot') == True and self.plot_counter < 6):
                        self.visual.create_sample(characteristic['norm'], 'norm'+str(self.plot_counter)+'.png')
                        self.visual.create_sample(fft, 'fft'+str(self.plot_counter)+'.png')
                    self.plot_counter += 1
                self.counter += 1
            elif (obj['action'] == 'reset' and self.cfg.getoption('cmdlopt', 'dict') == None):
                self.reset()
            elif (obj['action'] == 'stop'):
                self.running = False

            if (self.counter > 0 and meta != None):
                for m in meta:
                    if (m['token'] == 'start analysis'):
                        self.remove_silence(m)
                        if (self.cfg.getoption('cmdlopt', 'dict') == None):
                            self.analyze.do_analysis(self.compare.get_results(), self.character, self.rawbuf)
                        else:
                            self.util.store_raw_dict_entry(self.cfg.getoption('cmdlopt', 'dict'), self.raw_character)
                        self.reset()

        if (self.cfg.getbool('cmdlopt', 'wave') == True and len(self.rawbuf) > 0):
            self.save_wave_buf()

        self.queue.close()

        if (self.cfg.getbool('cmdlopt', 'plot') == True):
            self.visual.create_sample(self.rawfft, 'fft.png')

