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
  fft = [abs(i) for i in fft]
  chunked_fft_freq = [ ]
  chunked_fft_avg = [ ]
  steps = 50
  
  for i in range(0, len(fft), steps):
   chunk_avg = sum(fft[i:i+steps])/steps
   chunked_fft_freq.append(i)
   chunked_fft_avg.append(int(abs(chunk_avg)))

  right_trim = len(chunked_fft_avg)
  for i in range(len(chunked_fft_avg)-1,0,-1):
   if (chunked_fft_avg[i] == 0 and right_trim == i + 1):
    right_trim = i

  if (right_trim < len(chunked_fft_avg)):
   chunked_fft_freq = chunked_fft_freq[0:right_trim]
   chunked_fft_avg = chunked_fft_avg[0:right_trim]

  # we return nothing if the fft_freq len is below 3 as it is useless  
  if (len(chunked_fft_freq) <= 3):
   return None

  tendency_characteristic = self.get_tendency(tendency)

  # we return nothing if the avg is below 100 
  # or we got just below 20 frequencies
  # as this seems to be garbage
  if (tendency_characteristic['avg'] < 40 or len(chunked_fft_freq) < 20):
   return None

  fft_approach = self.get_approach(chunked_fft_avg)
  model_characteristic = {'fft_freq': len(chunked_fft_freq) , 'fft_approach': fft_approach, 'fft_avg': chunked_fft_avg, 'tendency': tendency_characteristic }

  return model_characteristic

 def get_approach(self, data):
  data = [abs(i) for i in data]
  ld = len(data)
  result = [ld] * ld
  m = max(data)+1
  l = 0
  f = 0
  pos = 0
  for z in range(0, ld):
   pos = z
   for i,a in enumerate(data):
    if (a < m and a > l):
     l = a
     pos = i
   result[pos] = z
   m = l
   l = 0
  return result

 def get_tendency(self, data):
  peaks = 0
  avg = (sum(data)/len(data))
  delta = data[0]-data[len(data)-1]
  lowercut = avg*1.1
  high = 0
  for n in data:
   if (n > high):
    high = n
   elif (n < lowercut):
    if (high > lowercut):
     peaks += 1
    high = 0
  tendency = { 'len': len(data), 'peaks': peaks, 'avg': avg, 'delta': delta }
  return tendency
  
