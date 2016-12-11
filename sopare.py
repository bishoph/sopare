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

import sys
import getopt
import sopare.util as util
import sopare.recorder as recorder
import sopare.err_logger as err_logger
from sopare.version import __version__

def main(argv):
    endless_loop = False
    debug = False
    outfile = None
    infile = None
    dict = None
    plot = False
    wave = False

    print ("sopare "+__version__)

    if (len(argv) > 0):
        try:                                
            opts, args = getopt.getopt(argv, "helpv~cos:w:r:t:d:",
             ["help", "error", "loop", "plot", "verbose", "wave", "create", "overview",
              "show=", "write=", "read=", "train=", "delete="
             ])
        except getopt.GetoptError:
            usage()
            sys.exit(2)
        for opt, arg in opts: 
            if (opt in ("-h", "--help")):
                usage()
                sys.exit(0)
            if (opt in ("-e", "--error")):
                errlog = err_logger.err_logger()
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
                recreate_dict(debug)
                sys.exit(0)
            if opt in ("-o", "--overview"):
                show_dict_ids(debug)
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
    recorder.recorder(endless_loop, debug, plot, wave, outfile, 
                      infile, dict)

def recreate_dict(debug):
    print ("recreating dictionary from raw input files...")
    utilities = util.util(debug)
    utilities.recreate_dict_from_raw_files()

def delete_word(dict, debug):
    if (dict != "*"):
        print ("deleting "+dict+" from dictionary")
    else:
        print ("deleting all enttries from dictionary")
    utilities = util.util(debug)
    utilities.deletefromdict(dict)

def show_word_entries(dict, debug):
    print (dict+" entries in dictionary:")
    print
    utilities = util.util(debug)
    utilities.showdictentry(dict)

def show_dict_ids(debug):
    print ("current entries in dictionary:")
    utilities = util.util(debug)
    utilities.showdictentriesbyid()

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
    print (" -d --delete [word]  : delete [word] from dictionary and exit.")
    print ("                       '*' deletes everyting!\n")

main(sys.argv[1:])
