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

class hatch():

    def __init__(self):
        self.plot_cache = [ ]
        self.key_value_store = { }

    def add(self, key, value):
        self.key_value_store[key] = value

    def get(self, key):
        if (key in self.key_value_store):
            return self.key_value_store[key]
        return None

    def extend_plot_cache(self, data):
        self.plot_cache.extend(data)

    def get_plot_cache(self):
        return self.plot_cache
