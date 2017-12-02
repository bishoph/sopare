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
import unittest
import pyaudio
import audioop
import math
import time
import sys
import test_multi
sys.path.append('../sopare')
import sopare.log
import sopare.config
import sopare.audio_factory

class test_audio(unittest.TestCase):

    SAMPLE_RATES = [ 8000, 11025, 12000, 16000, 22050, 32000, 44100, 48000 ]
    CHUNKS = [ 512, 1024, 2048, 4096, 8192 ]
    TEST_RESULTS = { }

    def __init__(self):
        print ("test_audio init...")
        self.good_sample_rates = [ ]
        self.good_chunks = [ ]
        self.silence = [ ]
        self.stream = None

        cfg = sopare.config.config()
        logger = sopare.log.log(True, False)
        cfg.addlogger(logger)

        self.audio_factory = sopare.audio_factory.audio_factory(cfg)
        self.queue = multiprocessing.JoinableQueue()
        self.multi = test_multi.multi(self.queue)

    def read(self, chunks, loops):
        test_result = False
        vol = 0
        try:
            for x in range(loops):
                buf = self.stream.read(chunks)
                self.queue.put(buf)
                current_vol = audioop.rms(buf, 2)
                if (current_vol > vol):
                    vol = current_vol
            self.silence.append(vol)
            test_result = True
            print ('Excellent. Got all '+str(chunks*loops) + ' chunks.')
        except IOError as e:
            test_result = False
            print ("Error: "+ str(e))
        return test_result

    def test_environment(self):
        self.assertGreaterEqual(multiprocessing.cpu_count(), 4, 'SOPARE requires a multiprocessor architecture and was tested with at least 4 cores (e.g. RPi2/3)')

    def test_sample_rates(self):
        print ('testing different SAMPLE_RATEs ... this may take a while!\n\n')
        for test_sample_rate in test_audio.SAMPLE_RATES:
            self.stream = self.audio_factory.open(test_sample_rate)
            if (self.stream != None):
                self.good_sample_rates.append(test_sample_rate)
                self.audio_factory.close()

    def test_chunks(self):
        print ('testing different CHUNK sizes ... this may take a while!\n\n')
        for good_sample_rate in self.good_sample_rates:
            for chunks in test_audio.CHUNKS:
                self.stream = self.audio_factory.open(good_sample_rate)
                if (self.stream != None):
                    if (good_sample_rate not in test_audio.TEST_RESULTS):
                        test_audio.TEST_RESULTS[good_sample_rate] = [ ]
                    read_test_result = ta.read(chunks, 10)
                    if (read_test_result == True):
                        self.good_chunks.append(chunks)
                        test_audio.TEST_RESULTS[good_sample_rate].append(chunks)
                self.audio_factory.close()

    def test_results(self):
        recommendations = { }
        found = False
        for sample_rate in test_audio.TEST_RESULTS:
            if (len(test_audio.TEST_RESULTS[sample_rate]) > 0):
                recommendations[sample_rate] = len(test_audio.TEST_RESULTS[sample_rate])
                found = True
        print ('\n\n')
        if (found == True):
            best = sorted(recommendations, key=recommendations.__getitem__, reverse = True)
            print ('Your sopare/config.py recommendations:\n')
            print ('SAMPLE_RATE = '+str(max(best)))
            print ('CHUNK = '+str(min(test_audio.TEST_RESULTS[best[0]])))
            treshold = int(math.ceil(max(self.silence) / 100.0)) * 100
            print ('THRESHOLD = '+str(treshold))
        else:
            print ('No recommendations, please fix your environment and try again!')
            print ('However, here are the sucessful tested sample rates:')
            print (str(test_audio.TEST_RESULTS))

    def stop(self):
        while (self.queue.qsize() > 0):
            time.sleep(.1) # wait for all threads to finish their work
        self.queue.close()
        self.multi.stop()
        self.queue.join_thread()
        self.audio_factory.close()
        self.audio_factory.terminate()
        sys.exit()

ta = test_audio()
ta.test_environment()
ta.test_sample_rates()
ta.test_chunks()
ta.test_results()
ta.stop()
