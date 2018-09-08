import plot
import talk
import numpy as np
import time
import csv
import matplotlib.pyplot as plt


import talk
from config._matplotlib_animation_patch import *
from config.constants import FILTER_WINDOW_SIZE, FILTER_CUTOFF, \
    PLOT_EVERY_TH, PLOT_X_SIZE, YMIN, YMAX


def main():
    # set plot parameters
    plt.style.use('dark_background')
    fig = plt.figure()
    signal_plot = plot.SignalPlot()

    controller = talk.ServoController()
    reader = talk.Reader(signal_plot)

    reader.start()

    while True:
        try:
            controller.angle = np.random.uniform(0, 180)
            controller.stiffness = np.random.uniform(-40, 40)
            if not controller._position_valid():
                continue

            time.sleep(5)

            with open("collected_data.txt", "a") as data:
                writer = csv.writer(data)
                writer.writerow([controller.angle,
                                 controller.stiffness,
                                 signal_plot.buff1[-1],     # or [0]
                                 signal_plot.buff2[-1],     # or [0]
                                 """Ania tu daj ten kat z kamery"""])

        except InterruptedError:
            # clean up
            reader.kill()
            reader.join()
            break
