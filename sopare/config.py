#########################################################
# Stream prep and silence configuration options #########
#########################################################

# Read chunk size
CHUNK = 512

# Sample rate
SAMPLE_RATE = 44100

# Volume threshold when audio processing starts / silence 
THRESHOLD = 400

# Silence time in seconds when analysis is called
MAX_SILENCE_AFTER_START = 3

# Time in seconds after the analysis is forced
MAX_TIME = 4

# Counter to stop processing and prepare more data
# Should be > LONG_SILENCE
SILENCE_COUNTER = 50

# Start the analysis after reaching LONG_SILENCE
LONG_SILENCE = 40



#########################################################
# Characteristic configuration options ##################
#########################################################

# Steps boil down the data into smaller chunks of data.
# Smaller steps mean more precision but require
# normally more learned entries in the dictionary.
# Progressive value is used if you want to pack not
# so relevant frequencies
PROGRESSIVE_FACTOR = 0
START_PROGRESSIVE_FACTOR = 8000
MIN_PROGRESSIVE_STEP = 100
MAX_PROGRESSIVE_STEP = 100

# Specifies freq ranges that are kept for further
# analysis. Freq outside of the ranges are set to zero.
# Human language can be found between 20 and 5000.
LOW_FREQ = 20
HIGH_FREQ = 1000

# Make use of Hann window function
HANNING = True

# Range factor for peaks
PEAK_FACTOR = 3



#########################################################
# Compare configuration options #########################
#########################################################

# Min. number of tokens to identify the beginning of a word
MIN_START_TOKENS = 3

# Min. value for potential beginning of a word
MARGINAL_VALUE = 0.5

# Minimal similarity across all comparison to
# identify a complete word across all tokens
MIN_CROSS_SIMILARITY = 0.6

# Min. post bias result for result consideration
BIAS = 0.3

# Calculation basis for token/word comparison
SIMILARITY_PEAKS = 1
SIMILARITY_HEIGHT = 0
SIMILARITY_DOMINANT_FREQUENCY = 0
