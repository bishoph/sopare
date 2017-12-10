This is the **SO**und **PA**ttern **RE**cognition project written in Python.
In a nutshell the project is able to listen in real time to microphone input
and detect patterns (like words) in the stream based on simple characteristics.
The output is an array of potential best guess matches. SOPARE works offline
and was tested successfully on a Raspberry Pi 2/3 and on a Banana Pi.


Here is an example output for the spoken words 'light off' in German:

```
 [u'licht', u'aus']

```


Scope and goals:
 
  * Real time audio processing
  * Must run on small credit card sized, ARM powered computers like Raspberry Pi, Banana Pi and alike
  * Pattern/voice recognition for only a few words
  * Must work offline without immanent dependencies to cloud APIs


Examples of use:

  * (Smart) home control
  * Voice controlled stuff like robots, smart mirrors and alike
  * Can be used in combination with any available cloud API or service like
     Alexa: https://developer.amazon.com/public/solutions/alexa/alexa-voice-service  
     Google: https://cloud.google.com/speech/  
     (and many more)  


Dependencies:

  * python
  * pyaudio (apt-get install python-pyaudio)
  * numpy (apt-get install python-numpy)
  * scipy (apt-get install python-scipy)
  * mathplot (apt-get install python-matplotlib)


Installation:

 Just checkout the project and resolve the dependencies:

 git clone https://github.com/bishoph/sopare.git

 Then you should create the following directories:

`
 tokens
`

` 
 samples
`

Abstract:

  * SOPARE detects words/patterns based on learned results
  * SOPARE must be trained to get results
  * SOPARE works offline
  * SOPARE recognizes words/patterns in real time and requires a multi core processor architecture
  * SOPARE is highly configurable for quick and dirty results as well as for more precise recognition
  * SOPARE was tested and developed with Python 2.7 on a Raspberry Pi 2
  * SOPARE comes with a very simple plugin interface for further processing


Next steps/TODOs:

  * Optimizations (e.g. word separation, performance)
  * Python3 compatibility and testing, install guides
  * Individual loglevels per class


Project status:

  * The project is able to learn sound patterns and to identify similar sounds even under different circumstances
  * Word separation is not perfect
  * Runs on several PIs 24/7 and controls smart home devices, smart mirrors, robots and alike
  * False positive rate is near zero for two-word recognition
  * Help needed in terms of python3 (numpy/scipy/pyaudio dependencies, installation, documentation, ...)


Usage:

```
 -h --help           : this help

 -l --loop           : loop forever

 -e --error          : redirect outpout to error.log
                       loglevel is forced to error!

 -p --plot           : plot results (only without loop option)

 -v --verbose        : enable verbose mode

 -~ --wave           : create *.wav files (token/tokenN.wav) for
                       each detected word

 -c --create         : create dict from raw input files

 -o --overview       : list all dict entries

 -s --show   [word]  : show detailed [word] entry information
                       '*' shows all entries!

 -w --write  [file]  : write raw to [dir/filename]

 -r --read   [file]  : read raw from [dir/filename]

 -t --train  [word]  : add raw data to raw dictionary file

 -d --delete [word]  : delete [word] from dictionary and exits.
                       '*' deletes everything!

 -i --ini    [file]  : use alternative configuration file

 -a --analysis       : show dictionary analysis and exits.

 -u --unit           : run unit tests
```


Quick start, useful commands and usage examples:

```
Here are some basic testing commands you can fire up to 
see if there are issues with the code or your environment.
The commands below help also to give you config recommendations
for your environment:

./sopare.py -u
python test/test_audio.py


Training, compiling and listening endless in debug mode.
(CTRL-c to stop):

python sopare.py -t "test"
python2 sopare.py -c
./sopare.py -v -l


Changing config options and new SOPARE versions require re-training.
Delete your training files and the dictionary entries before continue:

./sopare.py -d "*"
rm dict/*.raw
```


Find more detailed information on http://www.bishoph.org
