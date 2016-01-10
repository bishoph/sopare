# Used to learn, analyze and compare sounds.
# Position starts at 0 from the fft approach which means 
# that the first positions in the array are the most important ones.
IMPORTANCE = [ 10,9,8,7,6,5,4,3,2,1, 1,1,1,1,1,1,1,1,1,1 ]

# Tolerance table to find matches.
# Higher values mean more tolerance and therefor potential false positives!
# Position is taken from the fft approach which means that
# the first positions are the most important ones.
WITHIN_RANGE = [ 0,1,2,3,4,5 ]

# Learning curve. Smaller numbers learn slower but give you normally a better accuracy.
# As the current recognition is based on the fft approach for each token rather than 
# real values we just don't care much about this.
# If the comparator array is longer the value 0.1
# is used in the appropriate functions.
ACCURACY = [ 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1 ]
