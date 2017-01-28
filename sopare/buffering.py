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
import processing

class buffering(multiprocessing.Process):

    def __init__(self, queue, endless_loop, debug, plot, wave, outfile, dict):
        multiprocessing.Process.__init__(self, name="buffering queue")
        self.queue = queue
        self.endless_loop = endless_loop
        self.debug = debug
        self.plot = plot
        self.outfile = outfile
        self.proc = processing.processor(endless_loop, debug, plot, wave, outfile, dict, self)
        self.PROCESS_ROUND_DONE = False
        self.test_counter = 0
        self.start()
  
    def run(self):
        if (self.debug):
            print ("buffering queue runner")
        while True:
            buf = self.queue.get()
            if ((self.endless_loop == False or self.outfile != None) and self.PROCESS_ROUND_DONE):
                break
            self.proc.check_silence(buf)
        if (self.debug):
            print ("terminating queue runner")

    def flush(self, message):
        self.proc.stop(message)
 
    def stop(self):
        if (self.debug):
            print ("stop buffering")
        self.PROCESS_ROUND_DONE = True

  



