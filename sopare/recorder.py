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
import pyaudio
import logging
import numpy
import time
import sys
import io
import sopare.buffering
import sopare.config
import sopare.hatch
import sopare.visual

class recorder():

    def __init__(self, hatch):
        self.hatch = hatch
        self.FORMAT = pyaudio.paInt16
        # mono
        self.CHANNELS = 1
        self.pa = pyaudio.PyAudio()
        self.queue = multiprocessing.JoinableQueue()
        self.running = True
        self.visual = sopare.visual.visual()

        # logging ###################
        self.logger = self.hatch.get('logger').getlog()
        self.logger = logging.getLogger(__name__)

        self.buffering = sopare.buffering.buffering(self.hatch, self.queue)
        if (hatch.get('infile') == None):
            self.recording()
        else:
            self.stream = None
            self.readfromfile()

    def open(self):
        try:
            self.stream = self.pa.open(format = self.FORMAT,
                channels = 1,
                rate = sopare.config.SAMPLE_RATE,
                input = True,
                output = False)
        except IOError as e:
            self.logger.error("IOError: " + str(e))
            sys.exit(1)

    def debug_info(self):
        defaultCapability = self.pa.get_default_host_api_info()
        self.logger.debug(str(defaultCapability))
        self.logger.debug('SAMPLE_RATE: '+str(sopare.config.SAMPLE_RATE))
        self.logger.debug('CHUNK: '+str(sopare.config.CHUNK))

    def readfromfile(self):
        self.debug_info()
        self.logger.info("* reading file " + self.hatch.get('infile'))
        file = io.open(self.hatch.get('infile'), 'rb', buffering = sopare.config.CHUNK)
        while True:
            buf = file.read(sopare.config.CHUNK * 2)
            if buf:
                self.queue.put(buf)
                if (self.hatch.get('plot') == True):
                    data = numpy.fromstring(buf, dtype=numpy.int16)
                    self.hatch.extend_plot_cache(data)
            else:
                self.queue.close()
                break
        file.close()
        once = False
        if (self.hatch.get('plot') == True):
            self.visual.create_sample(self.hatch.get_plot_cache(), 'sample.png')
        while (self.queue.qsize() > 0):
            if (once == False):
                self.logger.debug('waiting for queue to finish...')
                once = True
            time.sleep(.1) # wait for all threads to finish their work
        self.queue.close()
        self.buffering.flush('end of file')
        self.logger.info("* done ")
        self.stop()
        sys.exit()

    def recording(self):
        self.open()
        self.debug_info()
        self.logger.info("start endless recording")
        while self.running:
            try:
                if (self.buffering.is_alive()):
                    buf = self.stream.read(sopare.config.CHUNK)
                    self.queue.put(buf)
                else:
                    self.logger.info("Buffering not alive, stop recording")
                    self.queue.close()
                    break
            except IOError as e:
                self.logger.warning("stream read error "+str(e))
                if (hasattr(sopare.config, 'STREAM_RECREATE') and sopare.config.STREAM_RECREATE == True):
                    self.logger.info('trying to recreate stream...')
                    self.stream.close()
                    self.open()
                    self.logger.info('...stream recreated.')
        self.stop()
        sys.exit()

    def stop(self):
        self.logger.info("stop endless recording")
        self.running = False
        try:
            self.queue.join_thread()
            self.buffering.terminate()
        except:
            pass
        if (self.stream != None):
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()
