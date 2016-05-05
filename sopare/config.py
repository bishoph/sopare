# Sample rate
SAMPLE_RATE = 44100

# Threshold
THRESHOLD = 500

# SIMILARITY calculation basis should be in sum 1
FFT_SIMILARITY = 0.5
TENDENCY_SIMILARITY = 0.2
OUTLINE_DISTANCE = 0.1
HIGH_MATCH_POINTS = 0.1
MATCH_POINTS = 0.1

# This value defines the marginal value that is needed
# for consideration if the analyzed result becomes a
# "pre_readable result"
MARGINAL_VALUE = 0.4

# This value defines the min value that is needed
# for consideration if the analyzed result becomes a
# "readable result"
MIN_READABLE_RESULT_VALUE = 0.6

# Last line of defence
SHAPE_SIMILARITY = 0.9

# Set to True for extra precision for similarity calculation.
# Set to False if you want more results but be aware that
# this could raise more false positives as well.
USE_LENGTH_SIMILARITY = True

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
FAST_HIGH_COMPARE_MARGINAL_VALUE = 0.8

# Number of matches that are taken into consideration
# for the first comparison and to get first results.
# Default: 5
FAST_HIGH_COMPARISON = 5

# This number calculates the threshold for consideration
# for the first comparison.
GET_HIGH_THRESHOLD = 4

# Steps boil down the data into smaller junks of data.
# Smaller steps means more precision but require
# normally more learned entries in the dictionary 
# We use a progressive value to get smaller steps in the
# low frequencies
PROGRESSIVE_FACTOR = 0.1
MIN_PROGRESSIVE_STEP = 20
MAX_PROGRESSIVE_STEP = 500

# If result are > CUT_RESULT_LENGTH results are cut
# to the CUT_RESULT_LENGTH length
CUT_RESULT_LENGTH = 80

# Used to analyze and compare sounds.
# Position starts at 0 from the fft approach which means 
# that the importance goes from left to right.
IMPORTANCE = [ 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1 ]

# Tolerance table to find matches.
# Higher values mean more tolerance and therefor potential false positives!
# Position is taken from the fft approach which means that
# the first positions are the most important ones.
WITHIN_RANGE = [ 1,2,2,2,2,3,3,3,3 ]

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
# Set to True if you have a use amount of
# entries and eventually performance issues.
# Compressing the dictionary also deals with
# outliers but could obiously lead to less matches.
COMPRESS_DICT = False
