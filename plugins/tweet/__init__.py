
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

# Simple twitter plugin
#
# To get this up and running on a Raspberry Pi 
# the following commands/packages are required
# 
# sudo apt-get install python-dev python-pip
# sudo pip install -U pip
# sudo pip install tweepy
# sudo apt-get install libffi-dev
# sudo pip install pyopenssl ndg-httpsclient pyasn1


import tweepy
import imp

api = None

try:
 # The following file must contain consumer_key, consumer_secret, access_token, access_token_secret
 # to be able to authentication against Twitter with oAuth
 SOPARE_PLUGIN_SECRETS = imp.load_source('sopare_plugin_secrets', '/etc/sopare/secrets.py')
 auth = tweepy.OAuthHandler(SOPARE_PLUGIN_SECRETS.consumer_key, SOPARE_PLUGIN_SECRETS.consumer_secret)
 auth.set_access_token(SOPARE_PLUGIN_SECRETS.access_token, SOPARE_PLUGIN_SECRETS.access_token_secret)
 api = tweepy.API(auth)
except:
 print ('An error occured while initializing the Twitter API. Continue anyway without tweeting!')

def run(data):
 # extract best match from results 
 map = [ ]
 best_match = [ ]
 for d in data:
  if (d[2] not in map):
   map.append(d[2])
 for m in map:
  pos = 0
  best = 0
  match = ''
  length = 0
  for d in data:
   if (m == d[2] and best < d[1]):
    pos = d[0]
    best = d[1]
    match = d[2]
    length = d[3]
  best_match.append([best, match, pos, length])
 best_match = sorted(best_match, key=lambda x: x[2])

 # eliminate double entries 
 matchpos = [ ]
 for match in best_match:
  if (match[2] not in matchpos):
   matchpos.append(match[2])
 if (len(matchpos) != len(best_match)):
  clean_best_match = [ ]
  for pos in matchpos:
   for match in best_match:
     if (pos == match[2]):
      clean_best_match.append(match)
      break
  best_match = clean_best_match

 # This is my beta test match list and we generate an status update
 # that is useful for testing purpose and does not reveal any real info
 matches = [ 'computer', 'licht', 'dach' ]
 m = 0
 status = ''
 last = 0
 ll = 0
 rl = 0
 gl = 0
 aus = False
 for i, match in enumerate(matches):
  for j, bm in enumerate(best_match):
   if (match == bm[1] and bm[0] > 100 and i == j):
    if (m == 0):
     status = str(j)+':'+str(bm[0])+':'+str(bm[2])
    else:
     status = status + ","+str(j)+':'+str(bm[0])+':'+str(bm[2])
     ll += bm[3]
     rl += (bm[2]-last)
    gl += bm[3]
    m += 1
    last = bm[2]
   elif ('aus' == bm[1]):
    aus = True
 status = status + ' / ' + str(ll) + '-' + str(rl) + '-' + str(gl)
 if (aus == True):
  status = status + ' *1*'

 if (m == len(matches)):
  tweet(status)

def tweet(status):
 if (api != None):
  api.update_status(status)
