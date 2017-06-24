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

import multiprocessing 
import util
import visual
import analyze
import characteristics
import uuid
import comparator
import config
import hatch

class worker(multiprocessing.Process):

    def __init__(self, hatch, queue):
        multiprocessing.Process.__init__(self, name="worker for filtered data")
        self.hatch = hatch
        self.queue = queue
        self.visual = visual.visual()
        self.util = util.util(self.hatch.get('debug'))
        self.analyze = analyze.analyze(self.hatch.get('debug'))
        self.compare = comparator.compare(self.hatch.get('debug'), self.util)
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
        if (self.hatch.get('wave') == True and len(self.rawbuf) > 0):
            self.save_wave_buf()
        self.rawbuf = [ ]
        #self.rawfft = [ ]
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
        silence = ((config.LONG_SILENCE * config.CHUNK) / 4096) - 4 # TODO: Find auto value or make configurable
        if (silence < 0):
            silence = 0
        for x in range(len(self.character) - 1, len(self.character) - silence, -1):
            if (x <= len(self.character)-1 and x > 0):
                del self.character[x]
        if (len(self.raw_character) > 0):
            for x in range(len(self.raw_character) - 1, len(self.raw_character) - silence , -1):
                del self.raw_character[x]


    def run(self):
        if (self.hatch.get('debug') == True):
            print ("worker queue runner started")
        while self.running:
            obj = self.queue.get()
            if (obj['action'] == 'data'):
                raw_token = obj['token']
                if (self.hatch.get('wave') == True or True): # TODO: "or True" is just temporary for testing. Must be removed later on!
                    self.rawbuf.extend(raw_token)
                fft = obj['fft']
                if (self.hatch.get('plot') == True):
                    self.rawfft.extend(fft)
                meta = obj['meta']
                norm = obj['norm']
                characteristic = obj['characteristic']
                self.character.append((characteristic, meta))
                self.compare.word(self.character)
                if (self.hatch.get('dict') != None):
                    self.raw_character.append({ 'fft': fft, 'norm': norm, 'meta': meta })
                if (characteristic != None):
                    if (self.hatch.get('debug') == True):
                        print ('characteristic = ' + str(self.counter) + ' ' + str(characteristic))
                        print ('meta = '+str(meta))
                    if (self.hatch.get('wave') == True):
                        self.util.savefilteredwave('token'+str(self.counter)+self.uid, raw_token)
                    if (self.hatch.get('plot') == True and self.plot_counter < 6):
                        self.visual.create_sample(characteristic['norm'], 'norm'+str(self.plot_counter)+'.png')
                        self.visual.create_sample(fft, 'fft'+str(self.plot_counter)+'.png')
                    self.plot_counter += 1
                self.counter += 1
            elif (obj['action'] == 'reset' and self.hatch.get('dict') == None):
                self.reset()
            elif (obj['action'] == 'stop'):
                self.running = False

            if (self.counter > 0 and meta != None):
                for m in meta:
                    if (m['token'] == 'start analysis'):
                        self.remove_silence(m)
                        if (self.hatch.get('dict') == None):
                            self.analyze.do_analysis(self.compare.get_results(), self.character, self.rawbuf)
                        else:
                            self.util.store_raw_dict_entry(self.hatch.get('dict'), self.raw_character)
                        self.reset()

        if (self.hatch.get('wave') == True and len(self.rawbuf) > 0):
            self.save_wave_buf()

        self.queue.close()

        if (self.hatch.get('plot') == True):
            self.visual.create_sample(self.rawfft, 'fft.png')

