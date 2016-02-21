#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015, 2016 Martin Kauss (yo@bishoph.org)

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
import condense
import util
import visual
import analyze
import characteristics
import uuid

class worker(multiprocessing.Process):

    def __init__(self, queue, debug, plot, dict, wave):
        multiprocessing.Process.__init__(self, name="worker for prepared queue")
        self.queue = queue
        self.debug = debug
        self.plot = plot
        self.dict = dict
        self.wave = wave
        self.visual = visual.visual()
        self.condense = condense.packing()
        self.util = util.util(debug, None)
        self.analyze = analyze.analyze(debug)
        self.characteristic = characteristics.characteristic(debug)
        self.running = True
        self.counter = 0
        self.reset_counter = 0
        self.rawbuf = [ ]
        self.reset()
        self.DICT = self.util.getDICT()
        self.start()

    def reset(self):
        self.counter = 0
        if (self.wave and len(self.rawbuf) > 0):
            self.save_wave_buf()
        self.rawbuf = [ ]
        self.rawfft = [ ]
        self.raw = [ ]
        self.fft = [ ]
        self.word_tendency = None
        self.character = [ ]
        self.uid = str(uuid.uuid4())
        self.analyze.reset()
        self.reset_counter += 1

    def save_wave_buf(self):
        self.util.savefilteredwave('filtered_results'+str(self.reset_counter), self.rawbuf)

    def run(self):
        if (self.debug):
            print ("worker queue runner started")
        while self.running:
            obj = self.queue.get()
            if (obj['action'] == 'data'):
                raw_token = obj['token']
                if (self.wave or True): # TODO: "or True" is just temporary for testing. Should be removed later on!
                    self.rawbuf.extend(raw_token)
                fft = obj['fft']
                if (self.plot):
                    self.rawfft.extend(fft)
                meta = obj['meta']
                for m in meta:
                    if (m['token'] != 'stop'):
                        if (m['token'] == 'word' or m['token'] == 'long silence'):
                            word_tendency = self.characteristic.get_word_tendency(m['peaks'])
                            m['word_tendency'] = word_tendency
                            if (word_tendency != None):
                                self.word_tendency = word_tendency
                raw_token_compressed = self.condense.compress(raw_token)
                raw_tendency = self.condense.model_tendency(raw_token_compressed)
                characteristic = self.characteristic.getcharacteristic(fft, raw_tendency)
                self.character.append((characteristic, meta))
                if (characteristic != None):
                    if (self.debug):
                        print ('characteristic = ' + str(self.counter) + ' ' + str(characteristic))
                        print ('meta = '+str(meta))
                    if (self.wave):
                        self.util.savefilteredwave('token'+str(self.counter)+self.uid, raw_token)
                    if (self.plot):
                        self.visual.create_sample(raw_tendency, 'token'+str(self.counter)+'.png')
                        self.visual.create_sample(fft, 'fft'+str(self.counter)+'.png')
                self.counter += 1
            elif (obj['action'] == 'reset' and self.dict == None):
                self.reset()
            elif (obj['action'] == 'stop'):
                self.analyze.do_analysis(self.character, None)
                self.running = False

            if (self.counter > 0 and meta != None):
                for m in meta:
                    if (m['token'] == 'long silence'):
                        if (self.dict == None):
                            self.analyze.do_analysis(self.character, self.rawbuf)
                            self.reset()

        # end of while
        for ch in self.character:
            c, meta = ch
            if (c != None):
                if (self.debug):
                    print (c)

        if (self.dict != None):
            self.DICT = self.util.learndict(self.character, self.word_tendency, self.dict)

        if (self.wave and len(self.rawbuf) > 0):
            self.save_wave_buf()

        self.queue.close()

        if (self.plot):
            self.visual.create_sample(self.rawfft, 'fft.png')

