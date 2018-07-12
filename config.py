"""
constants
"""

# serial
PORT = '/dev/ttyUSB0'
BAUDRATE = 74880

# plotting
PLOT_X_SIZE = 200
YMIN, YMAX = 500, 550
PLOT_EVERY_TH = 15       # for bigger, plot flows slower

# filter data
FILTER_WINDOW_SIZE = 120
FILTER_CUTOFF = .004    # gets wavy at >0.04
