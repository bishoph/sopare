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
MAX_SILENCE_AFTER_START = 1

# Time in seconds after the analysis is forced
MAX_TIME = 3.2

# Counter to stop processing and prepare more data
# Should be > LONG_SILENCE
SILENCE_COUNTER = 256

# Start the analysis after reaching LONG_SILENCE
LONG_SILENCE = 30

# Characteristic length
CHUNKS = 4096


#########################################################
# Characteristic configuration options ##################
#########################################################

# Steps boil down the data into smaller chunks of data.
# Smaller steps mean more precision but require
# normally more learned entries in the dictionary.
# Progressive value is used if you want to pack not
# so relevant frequencies
PROGRESSIVE_FACTOR = 0
START_PROGRESSIVE_FACTOR = 1000
MIN_PROGRESSIVE_STEP = 25
MAX_PROGRESSIVE_STEP = 25

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
MIN_START_TOKENS = 2

# Min. value for potential beginning of a word
MARGINAL_VALUE = 0.7

# Minimal similarity across all comparison to
# identify a complete word across all tokens
MIN_CROSS_SIMILARITY = 0.7

# Calculation basis or token/word comparison
SIMILARITY_NORM = 0.6
SIMILARITY_HEIGHT = 0.4
SIMILARITY_DOMINANT_FREQUENCY = 0

# Number of best matches to consider.
# Value must be > 0
# If not specified or value < 1 value is set to 1
NUMBER_OF_BEST_MATCHES = 2

# Min. distance to keep a word
MIN_LEFT_DISTANCE = 0.5
MIN_RIGHT_DISTANCE = 0.35

# Use given number as results to assembly result
# 0 for all predictions
MAX_WORD_START_RESULTS = 2
MAX_TOP_RESULTS = 3

# Enable or disable strict length check for words
STRICT_LENGTH_CHECK = True
# Value to soften the strict length check a bit to still
# get quite precise results but to be less strict
STRICT_LENGTH_UNDERMINING = 0

# Short term memory retention time in seconds. Zero to disable STM
STM_RETENTION = 1
