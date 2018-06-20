# serial
PORT = '/dev/ttyUSB0'
BAUDRATE = 74880

# plotting
PLOT_X_SIZE = 200
YMIN, YMAX = 505, 540
PLOT_EVERY_TH = 30       # for bigger, plot flows slower

# filter data
FILTER_WINDOW_SIZE = 120
FILTER_CUTOFF = .01    # gets wavy at >0.04
