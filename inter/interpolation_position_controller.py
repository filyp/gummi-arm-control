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
        self.result_angle = 90
        self.stiffness = 0

    def send(self, angle, stiffness):
        self.result_angle = angle
        self.stiffness = stiffness


    def run(self):
        controller = position_controller.PositionController()

        executor = InterpolationExecutor()
        executor.import_from_csv()
        f, _ = executor.interpolate_2()

        print(f)

        # f(angle) = (self.angle -> camera)
        # arg dla f sa stopnie, bo angle

        try:
            while True:
                x_a = scipy.optimize.fsolve(lambda x: f(x, self.stiffness) - int(self.result_angle), np.array([0]))
                servo_angle = int(x_a[0])
                print(servo_angle)

                try:
                    controller.send(servo_angle, self.stiffness)
                    print('sent')
                    break
                except ValueError:
                    print('dupa')
                    # chosen values were out of servos' range, so choose once again
                    pass
                time.sleep(1)

        except (KeyboardInterrupt, Exception) as e:
            print(e.__class__.__name__, str(e))


class InputReader(threading.Thread):
    def __init__(self, InterpolationController):
        threading.Thread.__init__(self)
        self.InterpolationController = InterpolationController

    def run(self):
        print('Enter angle (85 - 120):')
        while True:
            angle = input()
            print(angle)
            self.InterpolationController.result_angle = angle


# interpolation_controller = InterpolationPositionController()
# interpolation_controller.start()
#
# input_reader = InputReader(interpolation_controller)
# input_reader.start()
