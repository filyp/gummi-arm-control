import os
import dill
import numpy as np
import scipy.optimize
import glob

from src.benchmark.test_utils.approximation_stats import ApproximationStats
from src.constants import DEFAULT_FUNCTION, APPROXIMATING_FUNCTIONS_PATH, DATA_FOR_APPROXIMATION, \
    APPROXIMATION_DATA_PATH
from src.control.approximation.approximating_function_finder import ApproximatingFunctionFinder, \
    ApproximationDataImporter
from src.control.approximation.autocalibration import Autocalibration


class ServoAngleApproximator:
    def __init__(self, raw_controller, position_detector):
        self.arm_angle_approx = None
        self.raw_controller = raw_controller
        self.position_detector = position_detector

    @staticmethod
    def get_default_file():
        # TODO search for newest file (assume names can be incorrect) also TEST IT
        datafiles = glob.glob(DATA_FOR_APPROXIMATION)
        return sorted(datafiles)[-1]

    @staticmethod
    def file_exists(path, file_name):
        absolute_filename = os.path.join(path, file_name)
        return os.path.isfile(absolute_filename)

    @staticmethod
    def is_dir_empty(path):
        datafiles = glob.glob(path)
        print(len(datafiles))

        if len(datafiles) > 0:
            return False
        else:
            return True

    @staticmethod
    def load_approx_function(filename):
        absolute_filename = os.path.join(APPROXIMATING_FUNCTIONS_PATH, filename)
        with open(absolute_filename, 'rb') as file:
            return dill.load(file)

    def load_or_generate_approx_function(self, function_file=DEFAULT_FUNCTION, data_for_approx_file=None):
        print('in load and generate')
        if self.file_exists(APPROXIMATING_FUNCTIONS_PATH, function_file):
            self.arm_angle_approx = self.load_approx_function(function_file)
        else:
            if data_for_approx_file is not None and self.file_exists(APPROXIMATION_DATA_PATH, data_for_approx_file):
                print('not none and exists')
                path = APPROXIMATION_DATA_PATH + data_for_approx_file
            else:
                if self.is_dir_empty(DATA_FOR_APPROXIMATION):
                    print('dir empty')
                    autocalibration = Autocalibration(self.raw_controller, self.position_detector)
                    autocalibration.run()

                print('default file')
                path = self.get_default_file()
            importer = ApproximationDataImporter(path)
            importer.import_from_csv()
            finder = ApproximatingFunctionFinder(importer)
            finder.save_function_and_stats()

            # loading function
            self.arm_angle_approx = self.load_approx_function(function_file)

    def get_servo_angle(self, result_angle, stiffness):
        def f_to_solve(x):
            return self.arm_angle_approx(x, stiffness) - result_angle
        solutions = scipy.optimize.fsolve(f_to_solve, np.array([0]))
        servo_angle = solutions[0]
        return servo_angle
