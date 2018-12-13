import csv
import glob
import os

import dill
import numpy as np
import scipy.linalg
import logging

from src.benchmark.approximation_experiment.approximation_stats import ApproximationStats
from src.constants import APPROXIMATION_DATA_PATH, \
    DEFAULT_FUNCTION, APPROXIMATING_FUNCTIONS_PATH


def get_latest_approximation_file():
    """Get newest file with data for approximation.

    Looks for data in directory specified in src.constants.
    Assumes all file names in that directory have format:
    experiment_%Y-%m-%d %H:%M:%S.csv

    Returns:
        name of the newest file
        None, if there were no files

    """
    regex = os.path.join(APPROXIMATION_DATA_PATH, '*')
    datafiles = glob.glob(regex)
    if datafiles:
        return sorted(datafiles)[-1]
    else:
        return None


class ApproximationDataImporter:
    def __init__(self, file_name, threshold=3):
        self.file_name = file_name
        self.threshold = threshold
        self.angle = []
        self.stiffness = []
        self.camera = []

    def import_from_csv(self):
        with open(self.file_name) as datafile:
            logging.info(self.file_name)
            input_data = csv.DictReader(datafile)

            for row in input_data:
                if row['camera'] == 'nan':
                    continue
                self.angle.append(int(row['angle']))
                self.stiffness.append(int(row['stiffness']))
                self.camera.append(float(row['camera']))

        self.filter_outliers()

    def filter_outliers(self):
        # warning: very ugly function
        # compute Mahalanobis distance from the mean
        data = np.matrix([self.angle, self.stiffness, self.camera])
        covariance_matrix = np.cov(data)
        inv_covariance = np.linalg.inv(covariance_matrix)
        mean = np.mean(data, axis=1)

        filtered_values = []
        for data_tuple in data.transpose():
            euclidean_distance = data_tuple.transpose() - mean
            mahalanobis_deviation = euclidean_distance.transpose() \
                                    * inv_covariance \
                                    * euclidean_distance

            if mahalanobis_deviation[0, 0] < self.threshold:
                filtered_values.append(data_tuple.tolist()[0])

        self.angle, self.stiffness, self.camera = np.transpose(filtered_values)


class ApproximatingFunctionFinder:
    """Create approximating function from existing data."""
    def __init__(self, importer):
        self.coeffs = None
        self.importer = importer
        self.approximating_function = None

    def get_approximating_function(self):
        # c_ method added items along second axis
        data = np.c_[self.importer.angle, self.importer.stiffness, self.importer.camera]

        # Best-fit quadratic curve
        A = np.c_[np.ones(data.shape[0]), data[:, :2], np.prod(data[:, :2], axis=1), data[:, :2] ** 2]
        # Solve for a least squares estimate
        self.coeffs, _, _, _ = scipy.linalg.lstsq(A, data[:, 2])

        logging.info(self.coeffs)

        return lambda x, y: self.coeffs[4] * x ** 2. + \
                            self.coeffs[5] * y ** 2. + \
                            self.coeffs[3] * x * y + \
                            self.coeffs[1] * x + \
                            self.coeffs[2] * y + \
                            self.coeffs[0]

    def save_function_to_file(self, filename):
        absolute_filename = os.path.join(APPROXIMATING_FUNCTIONS_PATH, filename)
        with open(absolute_filename, 'wb') as file:
            dill.dump(self.approximating_function, file)

    def save_function_and_stats(self):
        self.approximating_function = self.get_approximating_function()
        self.save_function_to_file(DEFAULT_FUNCTION)
        logging.info(f'Function saved as {DEFAULT_FUNCTION}')

        # generate stats
        approx_stats = ApproximationStats(self.importer, self.approximating_function)
        approx_stats.plot_approximating_function()
        # approx_stats.plot_errors()
        approx_stats.plot_deviations_for_given_stiffness(10)


if __name__ == '__main__':
    path = get_latest_approximation_file()
    i = ApproximationDataImporter(path)
    i.import_from_csv()
    finder = ApproximatingFunctionFinder(i)
    logging.info(finder.approximating_function)
