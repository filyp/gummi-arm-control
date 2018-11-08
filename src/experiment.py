import csv
import time
import datetime

import numpy as np

from src import position_controller
from src import look

MAX_STIFFNESS = 90
FILENAME_BASE = 'data/experiment'


def main():
    controller = position_controller.PositionController()
    position_detector = look.PositionDetector(0.1)
    position_detector.start()

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    filename = '{} {}.csv'.format(FILENAME_BASE, timestamp)

    try:
        while True:
            try:
                angle = int(np.random.uniform(0, controller.MAX_ANGLE))
                stiffness = int(np.random.uniform(0, MAX_STIFFNESS))
                controller.send(angle, stiffness)
            except ValueError:
                continue

            time.sleep(1)

            angle_from_camera = position_detector.get_angle()

            with open(filename, 'a') as data:
                writer = csv.writer(data)
                row = [angle,
                       stiffness,
                       angle_from_camera]
                writer.writerow(row)
                print(row)

    except Exception as e:
        print(e.__class__.__name__, str(e))

    except KeyboardInterrupt:
        pass

    position_detector.kill()
    position_detector.join()


if __name__ == "__main__":
    main()
