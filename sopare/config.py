#########################################################
# Stream prep and silence configuration options #########
#########################################################

# Sample rate
SAMPLE_RATE = 44100

# Volume threshold when audio processing starts
THRESHOLD = 300

# Silence time in seconds when analysis is called
MAX_SILENCE_AFTER_START = 3

# Time in seconds after the analysis is forced
MAX_TIME = 5

# Counter to stop processing and prepare more data
# Should be > LONG_SILENCE
SILENCE_COUNTER = 100

# Tokenizer values to detect a new token
TOKEN_HIGH = 440
SILENCE = 5
# Start the analysis after reaching LONG_SILENCE
LONG_SILENCE = 60



#########################################################
# Characteristic configuration options ##################
#########################################################

# Steps boil down the data into smaller chunks of data.
# Smaller steps means more precision but require
# normally more learned entries in the dictionary.
# Progressive value is used if you want to pack not
# so relevant frequencies
PROGRESSIVE_FACTOR = .1
START_PROGRESSIVE_FACTOR = 2000
MIN_PROGRESSIVE_STEP = 20
MAX_PROGRESSIVE_STEP = 400

# Specifies freq ranges that are kept for further
# analysis. Freq outside of the ranges are set to zero.
# Human language can be found between 20 and 5000.
LOW_FREQ = 20
HIGH_FREQ = 5000

# Make use of Hann window function
HANNING = True

# Minimal FFT length for consideration
# Default: 12
MIN_FFT_LEN = 12

# Minimal FFT max. value for consideration
# Default: 5000
MIN_FFT_MAX = 5000

# Min. adaptive value to create a characteristic
# Default: TDB
MIN_ADAPTING = 5000



#########################################################
# Analysis configuration options ########################
#########################################################

# SIMILARITY calculation basis
FFT_SIMILARITY = 0.8
FFT_DISTANCE = 0.2
TENDENCY_SIMILARITY = 0

# First scan for candidates.
# We want to find potential positions as words tends to 
# overlap quite a bit. LEFT scans negative from a potential
# position, RIGHT positve. 
# Defaults: -3, 3
SEARCH_POTENTIAL_POSITION_LEFT = -3
SEARCH_POTENTIAL_POSITION_RIGHT = 4

# This value defines the marginal value that is needed
# for consideration if the analyzed result is added to
# "first_guess"
FAST_HIGH_COMPARE_MARGINAL_VALUE = 0.9

# Min. distance for consideration to keep "first_guess"
# potentials
MIN_DISTANCE = 0.6

# This values define the upper percentage for consideration
# if the analyzed result becomes a best_match value
MARGINAL_VALUE = 0.65
BEST_MATCH_VALUE = 0.7

# Set to True if you want to dilute results from 0-n in
# the similarity calculation.
POSITION_WEIGHTING = False

# This value defines the min value that is needed
# for consideration if the analyzed result becomes a
# "readable result"
MIN_READABLE_RESULT_VALUE = 0.8

# This values define the percentage needed when we
# compare the shapes of dict data against or analyzed
# data and the filled percentage of the results
# Last line of defense
SHAPE_SIMILARITY = 0.7
SHAPE_LENGTH_SIMILARITY = 0.4
RESULT_PERCENTAGE = 0.7

# Ignore MIN-/MAX token length check in get_readable results
SOFT_IGNORE_MIN_MAX = True



#########################################################
# Develop/experimental configuration options ############
#########################################################

# COMPRESS_DICT packs the dict. Simple as that.
# Note: Not yet functional implemented 
COMPRESS_DICT = False
