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

import pyaudio
import multiprocessing
import buffering
import time
import sys
import io
import config

class recorder:

    def __init__(self, endless_loop, debug, plot, wave, outfile, infile, dict):
        self.debug = debug
        self.plot = plot
        self.wave = wave
        self.outfile = outfile
        self.dict = dict
        self.FORMAT = pyaudio.paInt16
        # mono
        self.CHANNELS = 1
        self.pa = pyaudio.PyAudio()
        self.queue = multiprocessing.JoinableQueue()
        self.running = True
  
        if (debug):
            defaultCapability = self.pa.get_default_host_api_info()
            print defaultCapability

        self.stream = self.pa.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=config.SAMPLE_RATE,
                input=True,
                output=False,
                frames_per_buffer=config.CHUNK)

        self.buffering = buffering.buffering(self.queue, endless_loop, self.debug, self.plot, self.wave, self.outfile, self.dict)
        if (infile == None):
            self.recording()
        else:
            self.readfromfile(infile)

    def readfromfile(self, infile):
        print("* reading file "+infile)
        file = io.open(infile, 'rb', buffering=config.CHUNK)
        while True:
            buf = file.read(config.CHUNK * 2)
            if buf:
                self.queue.put(buf)
            else:
                self.queue.close()
                break
        file.close()
        while (self.queue.qsize() > 0):
            if (self.debug):
                print ('waiting for queue...')
            time.sleep(3) # wait for all threads to finish their work
        self.buffering.flush('end of file')
        print("* done ")
        self.stop()
        sys.exit()

    def recording(self):
        print("start endless recording")
        while self.running:
            try:
                if (self.buffering.is_alive()):
                    buf = self.stream.read(config.CHUNK)
                    self.queue.put(buf)
                else:
                    print ("Buffering not alive, stop recording")
                    self.queue.close()
                    break
            except IOError as e:
                print ("stream read error "+str(e))
        self.stop()
        sys.exit()

    def stop(self):
        print("stop endless recording")
        self.running = False
        try:
            self.queue.join_thread()
            self.buffering.terminate()
        except:
            pass
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
