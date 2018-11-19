import csv
import datetime
import time

import numpy as np

from src import look
from src import position_controller

MAX_STIFFNESS = 5
FILENAME_BASE = '../data/experiment'
DELAY_BETWEEN_ITERATIONS = 3
DETECTION_TIMEOUT = 1


def save_row(filename, row):
    """Append row to given .csv file.

    Args:
        filename: .csv file
        row: list of values

    """
    with open(filename, 'a') as data:
        writer = csv.writer(data)
        writer.writerow(row)
        print(row)


def experiment_iteration(controller, position_detector, filename):
    """Carry out one iteration of the experiment.

    Randomly choose angle and stiffness, and send them to arm.
    Give arm some time to change position.
    Measure what real angle the arm is at.
    Record these three values to a file.

    Args:
        controller: PositionController that communicates with servos
        position_detector: PositionDetector that reads arm angle from the camera
        filename: .csv file where data is saved

    """
    while True:
        angle = int(np.random.uniform(0, controller.MAX_ANGLE))
        stiffness = int(np.random.uniform(0, MAX_STIFFNESS))
        try:
            controller.send(angle, stiffness)
            break
        except ValueError:
            # chosen values were out of servos' range, so choose once again
            pass

    time.sleep(DELAY_BETWEEN_ITERATIONS)
    angle_from_camera = position_detector.get_angle()

    row = [angle, stiffness, angle_from_camera]
    save_row(filename, row)


def start(iteration_number=400):
    controller = position_controller.PositionController()
    position_detector = look.PositionDetector(DETECTION_TIMEOUT)
    position_detector.start()

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    filename = '{}_{}.csv'.format(FILENAME_BASE, timestamp)

    try:
        for i in range(iteration_number):
            experiment_iteration(controller, position_detector, filename)
    except KeyboardInterrupt:
        pass
    finally:
        position_detector.kill()
        position_detector.join()


if __name__ == "__main__":
    start()
