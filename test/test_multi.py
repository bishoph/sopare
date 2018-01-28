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
import numpy

class multi(multiprocessing.Process):

    def __init__(self, queue):
        multiprocessing.Process.__init__(self, name="multiprocessing buffering queue")
        self.queue = queue
        self.running = True
        self.start()
  
    def run(self):
        while (self.running == True or self.queue.is_alive()):
            buf = self.queue.get()
            data = numpy.fromstring(buf, dtype=numpy.int16)
            fft = numpy.fft.rfft(data)

    def stop(self):
        self.running = False
        self.terminate()
