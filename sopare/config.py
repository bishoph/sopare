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

# SIMILARITY calculation basis
FFT_SIMILARITY = .8
FFT_DISTANCE = .1
TENDENCY_SIMILARITY = .1

# Steps boil down the data into smaller chunks of data.
# Smaller steps means more precision but require
# normally more learned entries in the dictionary.
# Progressive value is used if you want to pack not
# so relevant frequencies
PROGRESSIVE_FACTOR = .01
START_PROGRESSIVE_FACTOR = 8000
MIN_PROGRESSIVE_STEP = 20
MAX_PROGRESSIVE_STEP = 20

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

# This number calculates the threshold for consideration
# for the first comparison.
GET_HIGH_THRESHOLD = 4



#########################################################
# Analysis configuration options ########################
#########################################################

# This value defines the marginal value that is needed
# for consideration if the analyzed result is added to
# "first_guess"
# (1)
FAST_HIGH_COMPARE_MARGINAL_VALUE = 0.9


# This values define the upper percentage for consideration
# if the analyzed result becomes a best_match value
# (2)
MARGINAL_VALUE = 0.5
BEST_MATCH_VALUE = 0.6


# Set to True if you want to dilute results from 0-n in
# the similarity calculation.
# (3)
POSITION_WEIGHTING = False

# This value defines the min value that is needed
# for consideration if the analyzed result becomes a
# "readable result"
# (3)
MIN_READABLE_RESULT_VALUE = 0.65

# Ignore MIN-/MAX token length check in pre_readable results
SOFT_IGNORE_MIN_MAX = True


# This values define the percentage needed when we
# compare the shapes of dict data against or analyzed
# data and the filled percentage of the results
# Last line of defense
SHAPE_SIMILARITY = 0.8
SHAPE_LENGTH_SIMILARITY = 0.75
RESULT_PERCENTAGE = 0.8

# Ignore MIN-/MAX token length check in get_readable results
SOFT_IGNORE_MIN_MAX = True



#########################################################
# Develop/experimental configuration options ############
#########################################################

# COMPRESS_DICT packs the dict. Simple as that.
# Note: Not yet functional implemented 
COMPRESS_DICT = False
