import os
import dill
import numpy as np
import scipy.optimize
import logging

from src.constants import DEFAULT_FUNCTION, APPROXIMATING_FUNCTIONS_PATH


class ServoAngleApproximator:
    def __init__(self):
        self.arm_angle_approx = None

    def load_approx_function(self, function_file=DEFAULT_FUNCTION):
        absolute_filename = os.path.join(APPROXIMATING_FUNCTIONS_PATH, function_file)
        with open(absolute_filename, 'rb') as file:
            self.arm_angle_approx = dill.load(file)

    def get_servo_angle(self, arm_angle, stiffness):
        def f_to_solve(x):
            return self.arm_angle_approx(x, stiffness) - arm_angle
        solutions = scipy.optimize.fsolve(f_to_solve, np.array([0]))
        servo_angle = solutions[0]
        return servo_angle


a = ServoAngleApproximator(None, None)
a.load_or_generate_approx_function()
x = a.get_servo_angle(20, 0)

print(x)