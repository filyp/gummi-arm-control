import os
import dill
import numpy as np
import scipy.optimize
import glob
import logging

from src.benchmark.test_utils.approximation_stats import ApproximationStats
from src.constants import DEFAULT_FUNCTION, APPROXIMATING_FUNCTIONS_PATH, APPROXIMATION_DATA_PATH
from src.control.approximation.approximating_function_finder import ApproximatingFunctionFinder, \
    ApproximationDataImporter
from src.control.approximation.autocalibration import Autocalibration
from src.control.approximation.approximating_function_finder import get_latest_approximation_file


class ServoAngleApproximator:
    def __init__(self):
        self.arm_angle_approx = None

    def load_approx_function(self, function_file=DEFAULT_FUNCTION):
        absolute_filename = os.path.join(APPROXIMATING_FUNCTIONS_PATH, function_file)
        with open(absolute_filename, 'rb') as file:
            self.arm_angle_approx = dill.load(file)

    def generate_approx_function(self, raw_controller, position_detector, approx_data_file_name=None):
        if approx_data_file_name:
            approx_data = os.path.join(APPROXIMATION_DATA_PATH, approx_data_file_name)
        else:
            approx_data = get_latest_approximation_file()
            if not approx_data:
                logging.info('No data for approximation found, gathering data first...')
                autocalibration = Autocalibration(raw_controller, position_detector)
                autocalibration.run()
                approx_data = get_latest_approximation_file()

        logging.info('Calculating approximating function...')
        importer = ApproximationDataImporter(approx_data)
        importer.import_from_csv()
        finder = ApproximatingFunctionFinder(importer)
        finder.save_function_and_stats()

    def get_servo_angle(self, arm_angle, stiffness):
        def f_to_solve(x):
            return self.arm_angle_approx(x, stiffness) - arm_angle
        solutions = scipy.optimize.fsolve(f_to_solve, np.array([0]))
        servo_angle = solutions[0]
        return servo_angle
