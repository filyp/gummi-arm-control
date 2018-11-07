import csv
import time

import numpy as np

from src import position_controller
from src import look

MAX_STIFFNESS = 90


def main():
    controller = position_controller.PositionController()
    # position_detector = look.PositionDetector(0.1)
    # position_detector.start()

    try:
        while True:
            try:
                angle = int(np.random.uniform(0, controller.MAX_ANGLE))
                stiffness = int(np.random.uniform(0, MAX_STIFFNESS))
                controller.send(angle, stiffness)
            except ValueError:
                continue

            print(angle, stiffness)
            time.sleep(1)

            # angle = None
            # while not angle:
            #     angle = position_detector.get_angle()
            #
            # with open("collected_data.csv", "a") as data:
            #     writer = csv.writer(data)
            #     row = [controller.angle,
            #            controller.stiffness,
            #            angle]
            #     writer.writerow(row)
            #     print(row)

    except Exception as e:
        print(e.__class__.__name__, str(e))

    except KeyboardInterrupt:
        pass

    # position_detector.kill()
    # position_detector.join()


if __name__ == "__main__":
    main()
