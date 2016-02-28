# This value defines the marginal value that is needed
# for consideration if the analyzed result becomes a
# "readable value"
MARGINAL_VALUE = 1

# Percentage of inaccuracy for fast high comparison 
# in first scan.
INACCURACY_FAST_HIGH_COMPARE = 20

# Percentage of inaccuracy for word comparison
INACCURACY = 20

# Boolean 
# If true the fuzzy matches are used to calculate points
# and to consider result. Based on learned data this
# can easily result in false positives.
USE_FUZZY = False

# This value defines the min value for a perfect
# token match consideration.
# Depends on learned data.
MIN_PERFECT_MATCHES_FOR_CONSIDERATION = 2

# If you have bigger tokens you should have bigger steps
# as bigger tokens contain more diversification
# Rule of thump:
# smaller steps == more precision
STEPS = 100

# Used to learn, analyze and compare sounds.
# Position starts at 0 from the fft approach which means 
# that the first positions in the array are the most important ones.
IMPORTANCE = [ 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1 ]

# Tolerance table to find matches.
# Higher values mean more tolerance and therefor potential false positives!
# Position is taken from the fft approach which means that
# the first positions are the most important ones.
WITHIN_RANGE = [ 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1 ]

# Learning curve. Smaller numbers learn slower but give you normally a better accuracy.
# As the current recognition is based on the fft approach for each token rather than 
# real values we just don't care much about this.
# If the comparator array is longer the value 0.1
# is used in the appropriate functions.
ACCURACY = [ 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1 ]

