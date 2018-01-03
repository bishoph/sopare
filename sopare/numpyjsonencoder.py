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

import base64
import json
import numpy

class numpyjsonencoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = numpy.ascontiguousarray(obj)
                if (cont_obj.flags['C_CONTIGUOUS']):
                    obj_data = cont_obj.data
                else:
                    raise Exception("numpyjsonencoder err: C_CONTIGUOUS not present in object!")
            data_base64 = base64.b64encode(obj_data)
            return dict(__ndarray__= data_base64, dtype = str(obj.dtype), shape = obj.shape)
        return json.JSONEncoder(self, obj)

def numpyjsonhook(obj):
    if isinstance(obj, dict) and '__ndarray__' in obj:
        data = base64.b64decode(obj['__ndarray__'])
        return numpy.frombuffer(data, obj['dtype']).reshape(obj['shape'])
    return obj

