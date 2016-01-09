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

import pyaudio
import multiprocessing
import buffering
import sys
import io

class recorder:

    def __init__(self, endless_loop, debug, plot, wave, outfile, infile, dict, THRESHOLD = 500):
        self.debug = debug
        self.plot = plot
        self.wave = wave
        self.outfile = outfile
        self.dict = dict
        self.CHUNK = 512
        self.FORMAT = pyaudio.paInt16
        # mono
        self.CHANNELS = 1
        self.RATE = 44100
        self.pa = pyaudio.PyAudio()
        self.queue = multiprocessing.Queue()
  
        if (debug):
            defaultCapability = self.pa.get_default_host_api_info()
            print defaultCapability

        self.stream = self.pa.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                output=False,
                frames_per_buffer=self.CHUNK)

        if (infile == None):
            self.buffering = buffering.buffering(self.queue, endless_loop, self.debug, self.plot, self.wave, self.outfile, self.dict, THRESHOLD)
            self.recording(endless_loop)
        else:
            self.readfromfile(infile, THRESHOLD)

    def readfromfile(self, infile, THRESHOLD):
        print("* reading file "+infile)
        import processing
        proc = processing.processor(False, self.debug, self.plot, self.wave, None, self.dict, None, THRESHOLD)
        file = io.open(infile, 'rb', buffering=self.CHUNK*2)
        while True:
            buf = file.read(self.CHUNK*2)
            if buf:
                proc.check_silence(buf)
            else:
                break
        file.close
        proc.stop("end of file")
        print("* done ")
        self.stop()
        sys.exit()

    def recording(self, endless_loop):
        print("start endless recording")
        while True:
            try:
                if (self.buffering.is_alive()):
                    buf = self.stream.read(self.CHUNK)
                    self.queue.put(buf) 
                else:
                    print ("Buffering not alive, stop recording")
                    break
            except IOError as e:
                print ("stream read error "+str(e))
                pass
        self.stop()
        sys.exit()

    def stop(self):
        print("stop endless recording")
        try:
            self.queue.cancel_join_thread()
            self.buffering.terminate()
        except:
            pass
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()





