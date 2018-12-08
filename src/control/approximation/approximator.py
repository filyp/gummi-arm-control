import os

import dill
import numpy as np
import scipy.optimize

from src.constants import DEFAULT_FUNCTION, APPROXIMATING_FUNCTIONS
from src.control.approximation.approximation_finder import ApproximatingFunctionFinder


class ServoAngleApproximator:
    def __init__(self):
        absolute_filename = os.path.join(APPROXIMATING_FUNCTIONS, DEFAULT_FUNCTION)
        if not os.path.isfile(absolute_filename):
            print('Training arm on collected values...')
            ApproximatingFunctionFinder()

        with open(absolute_filename, 'rb') as file:
            self.f = dill.load(file)

    def get_servo_angle(self, result_angle, stiffness):
        x_a = scipy.optimize.fsolve(lambda x: self.f(x, stiffness) - int(result_angle), np.array([0]))
        servo_angle = int(x_a[0])

        return servo_angle
