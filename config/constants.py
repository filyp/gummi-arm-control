"""
constants
change them for different behaviour
"""

import platform


# serial
BAUDRATE = 74880
MAX_ANGLE = 180
PORT = {
    'Linux': '/dev/ttyUSB0',
    'Darwin': '/dev/tty.wchusbserial1420'
}[platform.system()]

# plotting
PLOT_X_SIZE = 200       # horizontal resolution of the plot
PLOT_EVERY_TH = 15      # for bigger value, plot flows slower

# filter data
FILTER_WINDOW_SIZE = 160
FILTER_CUTOFF = .002    # plots get wavy at >0.04
