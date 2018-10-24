import csv
import time

import numpy as np

from src import talk, look


def main():
    controller = talk.ServoController()
    position_detector = look.PositionDetector(0.1)
    position_detector.start()

    try:
        while True:
            controller.angle = int(np.random.uniform(0, 180))
            controller.stiffness = int(np.random.uniform(0, 0))
            if not controller._position_valid():
                print('dupa expo')
                continue
            controller.send()
            time.sleep(2)

            angle = None
            while not angle:
                angle = position_detector.get_angle()

            with open("collected_data.csv", "a") as data:
                writer = csv.writer(data)
                row = [controller.angle,
                       controller.stiffness,
                       angle]
                writer.writerow(row)
                print(row)

    except (KeyboardInterrupt, Exception) as e:
        print(e.__class__.__name__, str(e))
        position_detector.kill()
        position_detector.join()


if __name__ == "__main__":
    main()
