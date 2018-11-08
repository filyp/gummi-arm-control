import csv
import time
import threading
import scipy.optimize
import numpy as np

from src import position_controller
from inter.interpolation import *


class InterpolationPositionController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.angle = 90

    def run(self):
        controller = position_controller.PositionController()

        executor = InterpolationExecutor()
        executor.import_from_csv()
        f, _ = executor.interpolate()

        # f(angle) = (self.angle -> camera)
        # arg dla f sa stopnie, bo angle

        try:
            while True:
                x_a = scipy.optimize.fsolve(lambda x: f(x) - (3.1415 * int(self.angle) / 180), np.array([0]))
                target_angle = x_a[0] * 180 / 3.1415

                angle = int(target_angle)
                stiffness = int(0)
                try:
                    controller.send(angle, stiffness)
                    break
                except ValueError:
                    # chosen values were out of servos' range, so choose once again
                    pass
                time.sleep(1)

        except (KeyboardInterrupt, Exception) as e:
            print(e.__class__.__name__, str(e))


class InputReader(threading.Thread):
    def __init__(self, InterpolationPositionController):
        threading.Thread.__init__(self)
        self.InterpolationPositionController = InterpolationPositionController

    def run(self):
        print('Enter angle (60 - 100):')
        while True:
            angle = input()
            self.InterpolationPositionController.angle = angle


interpolation_controller = InterpolationPositionController()
interpolation_controller.start()

# input_reader = InputReader(interpolation_controller)
# input_reader.start()
