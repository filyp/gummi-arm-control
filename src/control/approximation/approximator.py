import os

import dill
import numpy as np
import scipy.optimize

from src.constants import DEFAULT_FUNCTION, APPROXIMATING_FUNCTIONS
from src.control.approximation.approximating_function_finder import ApproximatingFunctionFinder


class ServoAngleApproximator:
    def __init__(self, function_file=DEFAULT_FUNCTION):
        """

        Args:
            function_file:

        Notes:
            Parameters passed to this method must be the same as
            passed to Configurator.turn_on_pid.
        """
        try:
            self.arm_angle_approx = self.load_approx_function(function_file)
        except FileNotFoundError:
            print('Training arm on collected values...')
            ApproximatingFunctionFinder()
            self.arm_angle_approx = self.load_approx_function(function_file)

    def load_approx_function(self, filename):
        absolute_filename = os.path.join(APPROXIMATING_FUNCTIONS, filename)
        with open(absolute_filename, 'rb') as file:
            return dill.load(file)

    def get_servo_angle(self, result_angle, stiffness):
        def f_to_solve(x):
            return self.arm_angle_approx(x, stiffness) - result_angle
        solutions = scipy.optimize.fsolve(f_to_solve, np.array([0]))
        servo_angle = solutions[0]
        return servo_angle
