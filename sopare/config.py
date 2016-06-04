# Sample rate
SAMPLE_RATE = 44100

# Threshold
THRESHOLD = 500

# SIMILARITY calculation basis
FFT_SIMILARITY = .7
TENDENCY_SIMILARITY = .3

# This value defines the marginal value that is needed
# for consideration if the analyzed result becomes a
# "pre_readable result"
MARGINAL_VALUE = 0.4

# This value defines the min value that is needed
# for consideration if the analyzed result becomes a
# "readable result"
MIN_READABLE_RESULT_VALUE = 0.5

# Last line of defence
SHAPE_SIMILARITY = 0.6

# Set to True if you want to dilute results from 0-n in
# the similarity calculation.
POSITION_WEIGHTING = True

# Boolean 
# If true the fuzzy matches are used to calculate points
# and to consider result. Based on learned data this
# can easily result in false positives.
# Default: False
USE_FUZZY = False

# This value defines the marginal value that is needed
# for consideration if the analyzed result is added to 
# "first_guess"
FAST_HIGH_COMPARE_MARGINAL_VALUE = 0.3

# Number of matches that are taken into consideration
# for the first comparison and to get first results.
# Default: 5
FAST_HIGH_COMPARISON = 20

# This number calculates the threshold for consideration
# for the first comparison.
GET_HIGH_THRESHOLD = 4

# Steps boil down the data into smaller junks of data.
# Smaller steps means more precision but require
# normally more learned entries in the dictionary 
# We use a progressive value to get smaller steps in the
# low frequencies
PROGRESSIVE_FACTOR = 0.1
MIN_PROGRESSIVE_STEP = 1
MAX_PROGRESSIVE_STEP = 1000

# Specifies freq ranges that are kept for further
# analysis. Freq outside of the ranges are set to zero
LOW_FREQ = 20
HIGH_FREQ = 5000

# Minimal FFT len for considerartion
# Default: 12
MIN_FFT_LEN = 12

# Minimal FFT max. value for consideration
# Default: ?
MIN_FFT_MAX = 5000

# COMPRESS_DICT packs the dict. Simple as that.
# Not yet implemented. Just for testing purpose.
COMPRESS_DICT = False
