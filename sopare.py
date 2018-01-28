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

import sys
import getopt
import sopare.config as config
import sopare.util as util
import sopare.recorder as recorder
import sopare.log as log
import test.unit_tests as tests
from sopare.version import __version__

def main(argv):
    endless_loop = False
    debug = False
    outfile = None
    infile = None
    dict = None
    plot = False
    wave = False
    error = False
    cfg_ini = None

    recreate = False
    unit = False

    print ("sopare "+__version__)

    if (len(argv) > 0):
        try:
            opts, args = getopt.getopt(argv, "ahelpv~cous:w:r:t:d:i:",
             ["analysis", "help", "error", "loop", "plot", "verbose", "wave", "create", "overview", "unit",
              "show=", "write=", "read=", "train=", "delete=", "ini="
             ])
        except getopt.GetoptError:
            usage()
            sys.exit(2)
        for opt, arg in opts: 
            if (opt in ("-h", "--help")):
                usage()
                sys.exit(0)
            if (opt in ("-e", "--error")):
                error = True
            if (opt in ("-l", "--loop")):
                endless_loop = True
            if (opt in ("-p", "--plot")):
                if (endless_loop == False):
                    plot = True
                else:
                    print ("Plotting only works without loop option!")
                    sys.exit(0)
            if (opt in ("-v", "--verbose")):
                debug = True
            if (opt in ("-~", "--wave")):
                wave = True
            if opt in ("-c", "--create"):
                recreate = True
            if opt in ("-o", "--overview"):
                show_dict_ids(debug)
                sys.exit(0)
            if opt in ("-a", "--analysis"):
                show_dict_analysis(debug)
                sys.exit(0)
            if opt in ("-s", "--show"):
                show_word_entries(arg, debug)
                sys.exit(0)
            if opt in ("-w", "--write"):
                outfile = arg
            if opt in ("-r", "--read"):
                infile = arg
            if opt in ("-t", "--train"):
                dict = arg
            if opt in ("-d", "--delete"):
                delete_word(arg, debug)
                sys.exit(0)
            if opt in ("-i", "--ini"):
                cfg_ini = arg
            if opt in ("-u", "--unit"):
                unit = True

    cfg = create_config(cfg_ini, endless_loop, debug, plot, wave, outfile, infile, dict, error)

    if (recreate == True):
        recreate_dict(debug, cfg)
        sys.exit(0)

    if (unit == True):
        unit_tests(debug, cfg)
        sys.exit(0)


    recorder.recorder(cfg)

def create_config(cfg_ini, endless_loop, debug, plot, wave, outfile, infile, dict, error):
    if (cfg_ini == None):
        cfg = config.config()
    else:
        cfg = config.config(cfg_ini)
    logger = log.log(debug, error, cfg)
    cfg.addsection('cmdlopt')
    cfg.setoption('cmdlopt', 'endless_loop', str(endless_loop))
    cfg.setoption('cmdlopt', 'debug', str(debug))
    cfg.setoption('cmdlopt', 'plot', str(plot))
    cfg.setoption('cmdlopt', 'wave', str(wave))
    cfg.setoption('cmdlopt', 'outfile', outfile)
    cfg.setoption('cmdlopt', 'infile', infile)
    cfg.setoption('cmdlopt', 'dict', dict)
    cfg.addlogger(logger)
    return cfg

def recreate_dict(debug, cfg):
    print ("recreating dictionary from raw input files...")
    utilities = util.util(debug, cfg.getfloatoption('characteristic', 'PEAK_FACTOR'))
    utilities.recreate_dict_from_raw_files()

def delete_word(dict, debug):
    if (dict != "*"):
        print ("deleting "+dict+" from dictionary")
    else:
        print ("deleting all enttries from dictionary")
    utilities = util.util(debug, None)
    utilities.deletefromdict(dict)

def show_word_entries(dict, debug):
    print (dict+" entries in dictionary:")
    print
    utilities = util.util(debug, None)
    utilities.showdictentry(dict)

def show_dict_ids(debug):
    print ("current entries in dictionary:")
    utilities = util.util(debug, None)
    utilities.showdictentriesbyid()

def show_dict_analysis(debug):
    print ("dictionary analysis:")
    utilities = util.util(debug, None)
    analysis = utilities.compile_analysis(utilities.getDICT())
    for id in analysis:
        print (id)
        for k, v in analysis[id].iteritems():
            print (' ' + str(k) + ' ' + str(v))

def unit_tests(debug, cfg):
    print ("starting unit tests...")
    tests.unit_tests(debug, cfg)
    print ("done.")

def usage():
    print ("usage:\n")
    print (" -h --help           : this help\n")
    print (" -l --loop           : loop forever\n")
    print (" -e --error          : redirect sdterr to error.log\n")
    print (" -p --plot           : plot results (only without loop option)\n")
    print (" -v --verbose        : enable verbose mode\n")
    print (" -~ --wave           : create *.wav files (token/tokenN.wav) for")
    print ("                       each detected word\n")
    print (" -c --create         : create dict from raw input files\n")
    print (" -o --overview       : list all dict entries\n")
    print (" -s --show   [word]  : show detailed [word] entry information")
    print ("                       '*' shows all entries!\n")
    print (" -w --write  [file]  : write raw to [dir/filename]\n")
    print (" -r --read   [file]  : read raw from [dir/filename]\n")
    print (" -t --train  [word]  : add raw data to raw dictionary file\n")
    print (" -d --delete [word]  : delete [word] from dictionary and exits.")
    print ("                       '*' deletes everything!\n")
    print (" -i --ini    [file]  : use alternative configuration file\n")
    print (" -a --analysis       : show dictionary analysis and exits.\n")
    print (" -u --unit           : run unit tests\n")

main(sys.argv[1:])
