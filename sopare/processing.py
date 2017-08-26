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

import audioop
import time
import prepare
import io
import config
import hatch

class processor():

    def __init__(self, hatch, buffering, live = True):
        self.append = False
        self.hatch = hatch
        self.out = None
        if (self.hatch.get('outfile') != None):
            self.out = io.open(self.hatch.get('outfile'), 'wb')
        self.buffering = buffering
        self.live = live
        self.timer = 0
        self.silence_timer = 0
        self.silence_counter = 0
        self.silence_buffer = [ ]
        self.prepare = prepare.preparing(self.hatch)

    def stop(self, message):
        if (self.hatch.get('debug') == True):
            print (message)
        if (self.out != None):
            self.out.close()
        self.append = False
        self.silence_timer = 0
        if (self.hatch.get('endless_loop') == False):
            self.prepare.stop()
        else:
            self.prepare.force_tokenizer()
        if (self.buffering != None):
            self.buffering.stop()

    def check_silence(self, buf):
        volume = audioop.rms(buf, 2)
        if (volume >= config.THRESHOLD):
            self.silence_timer = time.time()
            if (self.append == False):
                if (self.hatch.get('debug') == True):
                    print ('starting append mode')
                self.timer = time.time()
                for sbuf in self.silence_buffer:
                    self.prepare.prepare(sbuf, volume)
                self.silence_buffer = [ ]
            self.append = True
            self.silence_counter = 0
        else:
            self.silence_counter += 1
            self.silence_buffer.append(buf)
            if (len(self.silence_buffer) > 3):
                del self.silence_buffer[0]
        if (self.out != None and self.out.closed != True):
            self.out.write(buf)
        if (self.append == True):
            self.prepare.prepare(buf, volume)
        if (self.append == True and self.silence_timer > 0
        and self.silence_timer + config.MAX_SILENCE_AFTER_START < time.time()
        and self.live == True):
            self.stop("stop append mode because of silence")
        if (self.append == True and self.timer + config.MAX_TIME < time.time()
        and self.live == True):
            self.stop("stop append mode because time is up")
