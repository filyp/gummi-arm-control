import csv
import datetime
import time

import numpy as np

from interpolation.interpolation_position_controller import InterpolationPositionController
from src import look
from src import position_controller


MAX_ANGLE = 180
FILENAME_BASE = '../data/validation_experiment'
DELAY = 4
EXAMINE_ANGLE = 90
STIFFNESS = 5


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


def experiment_iteration(controller, interpolation_controller, position_detector, filename):
    """Carry out one iteration of the experiment.

    Randomly choose angle and stiffness, and send them to arm.
    Give arm some time to change position.
    Measure what real angle the arm is at.
    Record these three values to a file.

    Args:
        controller: PositionController that communicates with servos
        position_detector: PositionDetector that reads arm angle from the camera
        filename: .csv file where data is saved
        interpolation_controller: ...

    """
    while True:
        angle = int(np.random.uniform(0, MAX_ANGLE))
        try:
            controller.send(angle, STIFFNESS)
            break
        except ValueError:
            # chosen values were out of servos' range, so choose once again
            pass

    time.sleep(DELAY)

    angle_from_camera_prev = position_detector.get_angle()

    servo_angle = interpolation_controller.send(EXAMINE_ANGLE, STIFFNESS)

    time.sleep(DELAY)

    angle_from_camera = position_detector.get_angle()

    row = [angle, angle_from_camera_prev,  servo_angle, STIFFNESS, angle_from_camera]
    save_row(filename, row)


def main():
    controller = position_controller.PositionController()
    position_detector = look.PositionDetector(1)
    position_detector.start()

    interpolation_controller = InterpolationPositionController()

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    filename = '{} {}.csv'.format(FILENAME_BASE, timestamp)

    labels = ["prev_angle_servo", "prev_angle", "angle_servo", "stiffness", "angle"]
    save_row(filename, labels)

    try:
        while True:
            experiment_iteration(controller, interpolation_controller, position_detector, filename)
    except KeyboardInterrupt:
        pass
    finally:
        position_detector.kill()
        position_detector.join()


if __name__ == "__main__":
    main()
