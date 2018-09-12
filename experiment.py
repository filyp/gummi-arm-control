import plot
import talk
import numpy as np
import time
import csv
import matplotlib.pyplot as plt


import talk
from config._matplotlib_animation_patch import *
from config.constants import FILTER_WINDOW_SIZE, FILTER_CUTOFF, \
    PLOT_EVERY_TH, PLOT_X_SIZE


def main():
    controller = talk.ServoController()

    while True:
        try:
            controller.angle = int(np.random.uniform(0, 180))
            controller.stiffness = int(np.random.uniform(-40, 40))
            if not controller._position_valid():
                continue
            controller.send()

            time.sleep(5)

            with open("collected_data.csv", "a") as data:
                writer = csv.writer(data)
                writer.writerow([controller.angle,
                                 controller.stiffness,
                                 "kąt"])

        except InterruptedError:
            break


if __name__ == "__main__":
     main()