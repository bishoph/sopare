# Sample rate
SAMPLE_RATE = 44100

# Threshold
THRESHOLD = 500

# This value defines the marginal value that is needed
# for consideration if the analyzed result becomes a
# "readable value"
MARGINAL_VALUE = 20

# Percentage of inaccuracy for fast high comparison 
# in first scan.
# Default: 20
INACCURACY_FAST_HIGH_COMPARE = 20

# Percentage of inaccuracy for word comparison
# Default: 20
INACCURACY = 20

# Percentage of inaccuracy for tendency (peak degree)
# Default: .2
TENDENCY_INACCURACY = .2

# Boolean 
# If true the fuzzy matches are used to calculate points
# and to consider result. Based on learned data this
# can easily result in false positives.
# Default: False
USE_FUZZY = False

# Number of matches that are taken into consideration
# for the first comparison and to get first results.
# Default: 5
FAST_HIGH_COMPARISON = 5

# This number calculates the threshold for consideration
# for the first comparison.
# Default: 3
GET_HIGH_THRESHOLD = 3

# This value defines the min value for a perfect
# token match consideration.
# Depends on learned data.
MIN_PERFECT_MATCHES_FOR_CONSIDERATION = 2

# Steps boil down the data into smaller junks of data.
# Smaller steps means more precision but require
# normally more learned entries in the dictionary 
# We use a progressive value to get smaller steps in the
# low frequencies
PROGRESSIVE_FACTOR = 0.08
MIN_PROGRESSIVE_STEP = 10
MAX_PROGRESSIVE_STEP = 2000

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

# This removes n results from the left side of the 
# fft results. Should be consistent with your filter
REMOVE_LEFT_FFT_RESULTS = 20
