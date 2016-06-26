# Sample rate
SAMPLE_RATE = 44100

# Volume threshold when audio processing starts
THRESHOLD = 500

# Silence time in seconds when analysis is called
MAX_SILENCE_AFTER_START = 4

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

# SIMILARITY calculation basis
FFT_SIMILARITY = .8
FFT_DISTANCE = .1
TENDENCY_SIMILARITY = .1

# This value defines the marginal value that is needed
# for consideration if the analyzed result becomes a
# "pre_readable result"
MARGINAL_VALUE = 0.6

# This value defines the min value that is needed
# for consideration if the analyzed result becomes a
# "readable result"
MIN_READABLE_RESULT_VALUE = 0.6

# Last line of defense
SHAPE_SIMILARITY = 0.5

# Set to True if you want to dilute results from 0-n in
# the similarity calculation.
POSITION_WEIGHTING = False

# This value defines the marginal value that is needed
# for consideration if the analyzed result is added to 
# "first_guess"
FAST_HIGH_COMPARE_MARGINAL_VALUE = 0.3

# This number calculates the threshold for consideration
# for the first comparison.
GET_HIGH_THRESHOLD = 4

# Steps boil down the data into smaller chunks of data.
# Smaller steps means more precision but require
# normally more learned entries in the dictionary.
# Progressive value is used if you want to pack not
# so relavant frequencies
PROGRESSIVE_FACTOR = .05
START_PROGRESSIVE_FACTOR = 1000
MIN_PROGRESSIVE_STEP = 20
MAX_PROGRESSIVE_STEP = 200

# Specifies freq ranges that are kept for further
# analysis. Freq outside of the ranges are set to zero.
# Human language can be found bewtween 20 and 5000.
LOW_FREQ = 20
HIGH_FREQ = 5000

# Make use of Hann window function
HANNING = False

# Minimal FFT len for consideration
# Default: 12
MIN_FFT_LEN = 12

# Minimal FFT max. value for consideration
# Default: 5000
MIN_FFT_MAX = 5000

# COMPRESS_DICT packs the dict. Simple as that.
# Note: Not yet functional implemented 
COMPRESS_DICT = False
