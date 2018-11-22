import os

import dill
import numpy as np
import scipy.optimize

from interpolation import interpolation


class ServoAngleInterpolator:
    def __init__(self):
        if not os.path.isfile(interpolation.LEARNED_FUNCTION_FILE):
            print('Training arm on collected values...')
            interpolation.InterpolationExecutor()

        with open(interpolation.LEARNED_FUNCTION_FILE, 'rb') as file:
            self.f = dill.load(file)

    def get_servo_angle(self, result_angle, stiffness):
        x_a = scipy.optimize.fsolve(lambda x: self.f(x, stiffness) - int(result_angle), np.array([0]))
        servo_angle = int(x_a[0])

        return servo_angle
