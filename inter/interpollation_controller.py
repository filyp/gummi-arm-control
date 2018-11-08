import csv
import time
import threading
import scipy.optimize
import numpy as np

from src import talk, look
from inter.interpolation import *


class InterpolationController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.angle = 90

    def run(self):
        controller = talk.ServoController()

        executor = InterpolationExecutor()
        executor.import_from_csv()
        f, _ = executor.interpolate()

        # f(angle) = (self.angle -> camera)
        # arg dla f sa stopnie, bo angle

        try:
            while True:
                x_a = scipy.optimize.fsolve(lambda x: f(x) - (3.1415 * int(self.angle) / 180), np.array([0]))
                target_angle = x_a[0] * 180 / 3.1415

                controller.angle = int(target_angle)
                controller.stiffness = int(0)
                if not controller._position_valid():
                    print('error: not valid position')
                    continue
                controller.send()
                time.sleep(1)

        except (KeyboardInterrupt, Exception) as e:
            print(e.__class__.__name__, str(e))


class InputReader(threading.Thread):
    def __init__(self, InterpolationController):
        threading.Thread.__init__(self)
        self.InterpolationController = InterpolationController

    def run(self):
        print('Enter angle (60 - 100):')
        while True:
            angle = input()
            self.InterpolationController.angle = angle


interpolation_controller = InterpolationController()
interpolation_controller.start()

input_reader = InputReader(interpolation_controller)
input_reader.start()
