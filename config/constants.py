"""
constants
change them for different behaviour
"""

# serial
PORT = '/dev/tty.wchusbserial1420'
BAUDRATE = 74880
MAX_ANGLE = 180

# plotting
PLOT_X_SIZE = 200       # horizontal resolution of the plot
YMIN, YMAX = 500, 580
PLOT_EVERY_TH = 15      # for bigger value, plot flows slower

# filter data
FILTER_WINDOW_SIZE = 120
FILTER_CUTOFF = .004    # plots get wavy at >0.04
