import ast
import csv
import datetime
import time
import os

import numpy as np

from src.control.position_controller import PositionController
from src.constants import ACCURACY_DATA_PATH
MAX_ANGLE = 180

FILENAME_BASE = os.path.join(ACCURACY_DATA_PATH, 'accuracy_experiment')
DELAY = 4


def save_row(filename, row):
    """Append row to given .csv file.

    Args:
        filename: .csv file
        row: list of values

    """
    with open(filename, 'a+') as data:
        writer = csv.writer(data)
        writer.writerow(row)
        print(row)


def experiment_iteration(controller, approximation_controller, position_detector, filename, examine_angle, stiffness):
    """Carry out one iteration of the experiment.

    Randomly choose angle and stiffness, and send them to arm.
    Give arm some time to change position.
    Measure what real angle the arm is at.
    Record these three values to a file.

    Args:
        controller: PositionController that communicates with servos
        position_detector: PositionDetector that reads arm angle from the camera
        filename: .csv file where data is saved
        approximation_controller: ...

    """
    while True:
        angle = int(np.random.uniform(0, MAX_ANGLE))
        try:
            controller.send(angle, stiffness)
            break
        except ValueError:
            # chosen values were out of servos' range, so choose once again
            pass

    time.sleep(DELAY)

    angle_from_camera_prev = position_detector.get_angle()

    approximation_controller.send(examine_angle, stiffness)

    time.sleep(DELAY)

    angle_from_camera = position_detector.get_angle()

    row = [angle, angle_from_camera_prev, stiffness, angle_from_camera, examine_angle]
    save_row(filename, row)


def start(angle, stiffness_list):
    print(angle)
    print(stiffness_list)

    position_controller = PositionController()
    position_controller.load_config()

    # TODO add send_raw to PositionController instead of taking away its raw_controller
    controller = position_controller.raw_controller
    position_detector = position_controller.position_detector

    try:
        for stiffness in stiffness_list:
            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            filename = '{} {}.csv'.format(FILENAME_BASE, timestamp)

            labels = ["prev_angle_servo", "prev_angle", "stiffness", "angle", 'examine_angle']
            save_row(filename, labels)
            for x in range(0, 30):
                experiment_iteration(controller, position_controller, position_detector, filename, angle, stiffness)
    except KeyboardInterrupt:
        pass
    finally:
        position_detector.kill()
        position_detector.join()
