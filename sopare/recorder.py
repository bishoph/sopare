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
import pyaudio
import logging
import numpy
import time
import sys
import io
import sopare.audio_factory
import sopare.buffering
import sopare.visual

class recorder():

    def __init__(self, cfg):
        self.cfg = cfg
        self.audio_factory = sopare.audio_factory.audio_factory(cfg)
        self.queue = multiprocessing.JoinableQueue()
        self.running = True
        self.visual = sopare.visual.visual()
        self.logger = self.cfg.getlogger().getlog()
        self.logger = logging.getLogger(__name__)
        self.buffering = sopare.buffering.buffering(self.cfg, self.queue)

        if (self.cfg.getoption('cmdlopt', 'infile') == None):
            self.recording()
        else:
            self.readfromfile()

    def debug_info(self):
        self.logger.debug('SAMPLE_RATE: '+str(self.cfg.getintoption('stream', 'SAMPLE_RATE')))
        self.logger.debug('CHUNK: '+str(self.cfg.getintoption('stream', 'CHUNK')))

    def readfromfile(self):
        self.debug_info()
        self.logger.info("* reading file " + self.cfg.getoption('cmdlopt', 'infile'))
        file = io.open(self.cfg.getoption('cmdlopt', 'infile'), 'rb', buffering = self.cfg.getintoption('stream', 'CHUNK'))
        while True:
            buf = file.read(self.cfg.getintoption('stream', 'CHUNK') * 2)
            if buf:
                self.queue.put(buf)
                if (self.cfg.getbool('cmdlopt', 'plot') == True):
                    data = numpy.fromstring(buf, dtype=numpy.int16)
                    self.visual.extend_plot_cache(data)
            else:
                self.queue.close()
                break
        file.close()
        once = False
        if (self.cfg.getbool('cmdlopt', 'plot') == True):
            self.visual.create_sample(self.visual.get_plot_cache(), 'sample.png')
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
        self.stream = self.audio_factory.open(self.cfg.getintoption('stream', 'SAMPLE_RATE'))
        self.debug_info()
        self.logger.info("start endless recording")
        while self.running:
            try:
                if (self.buffering.is_alive()):
                    buf = self.stream.read(self.cfg.getintoption('stream', 'CHUNK'))
                    self.queue.put(buf)
                else:
                    self.logger.info("Buffering not alive, stop recording")
                    self.queue.close()
                    break
            except IOError as e:
                self.logger.warning("stream read error "+str(e))
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
        self.audio_factory.close()
        self.audio_factory.terminate()
