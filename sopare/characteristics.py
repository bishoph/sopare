#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Martin Kauss (yo@bishoph.org)

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

class characteristic:

 def __init__(self, debug):
  self.debug = debug

 def getcharacteristic(self, fft, tendency):
  chunked_fft_freq = [ ]
  chunked_fft_avg = [ ]
  fft = abs(fft)
  fft_max = max(fft)
  fft_min = min(fft)
  fft_avg = sum(fft)/len(fft)
  steps = 100
  
  for i in range(0, len(fft), steps):
   chunk_sum = int(sum(fft[i:i+steps]))
   chunk_avg = int(sum(fft[i:i+steps])/steps)
   if (chunk_avg > fft_avg):
    chunked_fft_freq.append(i)
    chunked_fft_avg.append(chunk_avg)
  
  if (len(chunked_fft_freq) <= 3):
   return None
  tendency_characteristic = self.get_tendency(tendency)
  model_characteristic = {'fft_freq': chunked_fft_freq, 'fft_avg': chunked_fft_avg, 'tendency': tendency_characteristic }
   
  return model_characteristic

 def get_tendency(self, tendency):
  tendency_characteristic = [ ]
  peak = max(tendency)
  lowercut = peak  / 4
  high = 0
  highpos = 0
  pos = 0
  toppeaks = 0
  peaks = 0
  for n in tendency:
   if (n > high):
    high = n
    highpos = pos
    currentpeak = pos
    peaks += 1
   elif (n < lowercut):
    if (high > 0):
     toppeaks += 1
     high = 0
   pos += 1
  tendency_characteristic.append(peaks)
  tendency_characteristic.append(toppeaks)
  return tendency_characteristic
