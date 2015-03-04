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

 def getcharacteristic(self, tendency_model, dict_entry, learn):
  model_characteristic = [ ]
  length = len(tendency_model)
  peak = max(tendency_model)
  uppercut = peak / 3
  lowercut = peak  / 4
  top = [ ]
  highfreq = 0
  high = 0
  highpos = 0
  peaks = 0
  base = 0
  firstpeak = 0
  lastpeak = 0
  currentpeak = 0
  pos = 0
  for n in tendency_model:
   if (n > uppercut):
    highfreq += 1
    if (pos > 0 and firstpeak == 0):
     firstpeak = pos
    if (n > high):
     high = n
     highpos = pos
    currentpeak = pos
    peaks += 1
   elif (n < lowercut):
    if (high > 0):
     top.append([high, highpos])
    base += 1
    high = 0
   pos += 1
  lastpeak = currentpeak
  peakspace = lastpeak - firstpeak

  topspace = 0
  topstart = 0
  topend = 0
  if (len(top) >= 1):
   if (len(top) == 1):
    topspace = top[0][1]
   else:
    topspace = top[len(top)-1][1]-top[0][1]
   topstart = top[0][1]
   topend = top[len(top)-1][1]
  print ("topspace = "+str(topspace))
  min_length = length
  max_length = length
  min_peaks = len(top)
  max_peaks = len(top)
  min_topstart = topstart
  max_topstart = topstart
  min_topend = topend
  max_topend = topend
  min_base = base
  max_base = base
  min_topspace = topspace
  max_topspace = topspace
  min_peak = peak
  max_peak = peak 
  min_highfreq = highfreq
  max_highfreq = highfreq

  if (dict_entry != None):
   for elements in dict_entry:
    if ('min_length' in elements):
     min_length = elements['min_length']
    if ('max_length' in elements):
     max_length = elements['max_length']
    if ('min_peaks' in elements):
     min_peaks = elements['min_peaks']
    if ('max_peaks' in elements):
     max_peaks = elements['max_peaks']
    if ('min_topstart' in elements):
     min_topstart = elements['min_topstart']
    if ('max_topstart' in elements):
     max_topstart = elements['max_topstart']
    if ('min_topend' in elements):
     min_topend = elements['min_topend']
    if ('max_topend' in elements):
     max_topend = elements['max_topend']
    if ('min_base' in elements):
     min_base = elements['min_base']
    if ('max_base' in elements):
     max_base = elements['max_base']
    if ('min_topspace' in elements):
     min_topspace = elements['min_topspace']
    if ('max_topspace' in elements):
     max_topspace = elements['max_topspace']
    if ('min_peak' in elements):
     min_peak = elements['min_peak']
    if ('max_peak' in elements):
     min_peak = elements['max_peak']
    if ('min_highfreq' in elements):
     min_highfreq = elements['min_highfreq']
    if ('max_highfreq' in elements):
     max_highfreq = elements['max_highfreq']

   if (length < min_length):
    min_length = length
   if (length > max_length):
    max_length = length
   
   if (len(top) < min_peaks):
    min_peaks = len(top)
   if (len(top) > max_peaks):
    max_peaks = len(top)
   
   if (topstart < min_topstart):
    min_topstart = topstart
   if (topstart > max_topstart):
    max_topstart = topstart

   if (topend < min_topend):
    min_topend = topend
   if (topend > max_topend):
    max_topend = topend

   if (base < min_base):
    min_base = base
   if (base > max_base):
    max_base = base

   if (topspace < min_topspace):
    min_topspace = topspace
   if (topspace > max_topspace):
    max_topspace = topspace

   if (peak < min_peak):
    min_peak = peak
   if (peak > max_peak):
    max_peak = peak

   if (highfreq < min_highfreq):
    min_highfreq = highfreq
   if (highfreq > max_highfreq):
    max_highfreq = highfreq

  if (learn):
   model_characteristic.append({'min_length': min_length, 'max_length': max_length, 'min_peaks': min_peaks, 'max_peaks': max_peaks, 'min_topstart': min_topstart, 'max_topstart': max_topstart, 'min_topend': min_topend, 'max_topend': max_topend, 'min_base': min_base, 'max_base': max_base, 'min_topspace': min_topspace, 'max_topspace': max_topspace, 'min_peak': min_peak, 'max_peak': max_peak, 'min_highfreq': min_highfreq, 'max_highfreq': max_highfreq})
  else:
   model_characteristic.append({'max': peak, 'base': base, 'peakspace': peakspace, 'peaks': len(top), 'length': length, 'topstart': topstart, 'topend': topend, 'topspace': topspace, 'highfreq': highfreq})

  return model_characteristic
