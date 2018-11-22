import os

import dill
import numpy as np
import scipy.optimize

from approximation import approximation


class ServoAngleInterpolator:
    def __init__(self):
        if not os.path.isfile(approximation.LEARNED_FUNCTION_FILE):
            print('Training arm on collected values...')
            approximation.ApproximationExecutor()

        with open(approximation.LEARNED_FUNCTION_FILE, 'rb') as file:
            self.f = dill.load(file)

    def get_servo_angle(self, result_angle, stiffness):
        x_a = scipy.optimize.fsolve(lambda x: self.f(x, stiffness) - int(result_angle), np.array([0]))
        servo_angle = int(x_a[0])

        return servo_angle
