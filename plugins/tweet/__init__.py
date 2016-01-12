
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
import uuid

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

def run(analyzed_results, data):
    # extract best match from results 
    best_match = [ ]
    best_match = sorted(analyzed_results, key=lambda x: -x[1])

    # eliminate double entries 
    matchpos = [ ]
    for match in best_match:
        if (match[0] not in matchpos):
            matchpos.append(match[0])
    if (len(matchpos) != len(best_match)):
        clean_best_match = [ ]
        for pos in matchpos:
            for match in best_match:
                if (pos == match[0]):
                    clean_best_match.append(match)
                    break
        best_match = clean_best_match

    mapper = [ ]
    sorted_match = [ -1 ] * len(data)
    for i, bm in enumerate(best_match):
        if (bm[1] > 200):
            for a in range(bm[0], bm[0]+bm[3]):
                if (bm[2] not in mapper and a < len(sorted_match)):
                    sorted_match[a] = i
            mapper.append(bm[2])

    readable_results = ''
    last_word = ''
    for i in sorted_match:
        if (i >=0):
            text_result = best_match[i][2]
            if (text_result != last_word):
                readable_results += text_result
            last_word = text_result

    status = None
    if (readable_results == 'computerlichtaus'):
        status = '0:'+str(uuid.uuid4())
    elif (readable_results == 'computerlichtdach'):
        status = '1:'+str(uuid.uuid4())
    if (status != None):
        tweet(status)

def tweet(status):
    if (api != None):
        api.update_status(status)
