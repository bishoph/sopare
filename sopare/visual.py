#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 - 2018 Martin Kauss (yo@bishoph.org)

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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplot
from sopare.path import __plotdestination__

class visual:

    def __init__(self):
        self.plot_cache = [ ]

    def create_sample(self, data, filename):
        pyplot.plot(data)
        pyplot.savefig(__plotdestination__+filename)
        pyplot.clf()

    def extend_plot_cache(self, data):
        self.plot_cache.extend(data)

    def get_plot_cache(self):
        return self.plot_cache
