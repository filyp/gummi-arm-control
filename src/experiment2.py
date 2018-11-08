import csv
import time

import numpy as np

from src import talk, look

STIFFNESS = 10
ANGLE = 50
COUNTER = 20


def main():
    controller = talk.ServoController()
    position_detector = look.PositionDetector(0.1)
    position_detector.start()

    measurement_counter = 0

    try:
        while measurement_counter < COUNTER:
            controller.angle = int(np.random.uniform(0, 180))
            controller.stiffness = STIFFNESS
            if not controller._position_valid():
                continue
            # wysylanie w petli
            controller.send()
            time.sleep(2)

            controller.angle = ANGLE
            controller.stiffness = STIFFNESS
            if not controller._position_valid():
                continue
            controller.send()
            time.sleep(2)

            angle = None
            while not angle:
                angle = position_detector.get_angle()

            with open("collected_data_2.csv", "a") as data:
                writer = csv.writer(data)
                row = [controller.stiffness,
                       ANGLE,
                       angle]
                writer.writerow(row)
                print(row)

            measurement_counter += 1

    except (KeyboardInterrupt, Exception) as e:
        print(e.__class__.__name__, str(e))
        position_detector.kill()
        position_detector.join()


if __name__ == "__main__":
    main()
