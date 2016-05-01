This is the **SO**und **PA**ttern **RE**cognition project written in Python.
In a nutshell the project is able to listen in real time to microphone input
and detect patterns (like words) in the stream based on simple characteristics.
The output is an array of potential best guess matches. SoPaRe works offline
and was tested successfully on a Raspberry Pi 2 and on a Banana Pi. 


Here is an example output for the words 'light off' in German:

```
 [u'licht', u'aus']

```

Find more detailed information on http://www.bishoph.org and https://sway.com/BQ8uXDse9LLhL0Zf


Scope and goals:
 
  * Real time audio processing
  * Must run on small credit card sized, ARM powered computers like Raspberry Pi, Banana Pi and alike
  * Pattern/voice recognition for only a few words
  * Must work offline without immanent dependencies to cloud APIs


Examples of use:

  * (Smart) home control
  * Voice controlled stuff like robots
  * Can be used in combination with any available cloud API or service like
     Alexa: https://developer.amazon.com/public/solutions/alexa/alexa-voice-service  
     Google: https://cloud.google.com/speech/  
     (and many more)  
     e.g. to listen to a special pattern upfront
  

Dependencies:

  * Python
  * pyaudio (apt-get install python-pyaudio)
  * numpy (apt-get install python-numpy)
  * scipy (apt-get install python-scipy)
  * mathplot (apt-get install python-matplotlib)

  
Installation:

 Just checkout the project and resolve the dependencies:

 git clone https://github.com/bishoph/sopare.git .

 Then you should create the following directories:

`
 tokens
`

` 
 samples
`

Next steps/TODOs:

  * Optimizations, testing and bugfixing
  * Speed up first_scan 
  * Work on sanity checks, config options
  * Stop/timeout in analysis combo needs overhaul

Project status:

  * The project is able to learn sound patterns and to identify similar sounds even under different circumstances.
  * False positives still occur sometimes.
  * Currently the project is in a test and optimization phase.


Usage:

```
 -h --help            : this help

 -e --endless         : loop forever

 -p --plot            : plot results (only without loop option)

 -v --verbose         : enable verbose mode

 -w --wave            : creates wav files (token/tokenN.wav) for
                         each detected word

 -s --show            : shows detailed [dict] entry information
                         '*' shows all entries!

 -c --content         : list all dict entries

 -o --out [samples/filename]  : write to [samples/filename]

 -i --in [samples/filename]   : read [samples/filename]

 -l --learn [word]    : adds raw data to raw dictionary file.
                         (only without loop option)

 -r --recreate_dict   : recreates dict from raw input files.
                         should be used when changing
                         config options.
                         Please note that all raw files are
                         considered and compiled into the dict!
                         (only without loop option)

 -d --delete [word]   : delete [word] from dictionary and exit.
                         '*' deletes everyting!
```

