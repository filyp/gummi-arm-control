import csv
import datetime
import time

import numpy as np

from src import look
from src import position_controller


MAX_STIFFNESS = 90
FILENAME_BASE = 'data/experiment'
DELAY_BETWEEN_ITERATIONS = 1


def save_row(filename, row):
    with open(filename, 'a') as data:
        writer = csv.writer(data)
        writer.writerow(row)
        print(row)


def experiment_iteration(controller, position_detector, filename):
    angle = int(np.random.uniform(0, controller.MAX_ANGLE))
    stiffness = int(np.random.uniform(0, MAX_STIFFNESS))
    try:
        controller.send(angle, stiffness)
    except ValueError:
        return

    time.sleep(DELAY_BETWEEN_ITERATIONS)
    angle_from_camera = position_detector.get_angle()

    row = [angle, stiffness, angle_from_camera]
    save_row(filename, row)


def main():
    controller = position_controller.PositionController()
    position_detector = look.PositionDetector(0.1)
    position_detector.start()

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    filename = '{} {}.csv'.format(FILENAME_BASE, timestamp)

    try:
        while True:
            experiment_iteration(controller, position_detector, filename)
    except KeyboardInterrupt:
        pass
    finally:
        position_detector.kill()
        position_detector.join()


if __name__ == "__main__":
    main()
