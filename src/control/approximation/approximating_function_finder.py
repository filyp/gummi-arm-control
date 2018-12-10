import csv
import glob
import os
import textwrap

import dill
import matplotlib.pyplot as plt
import numpy as np
import scipy.linalg
from scipy.stats import binned_statistic
from mpl_toolkits.mplot3d import Axes3D


from src.benchmark import collect_data_for_approximation
from src.constants import DATA_FOR_APPROXIMATION, \
    DEFAULT_FUNCTION, APPROXIMATING_FUNCTIONS_PATH

def get_default_file():
    # TODO search for newest file (assume names can be incorrect) also TEST IT
    datafiles = glob.glob(DATA_FOR_APPROXIMATION)
    return sorted(datafiles)[-1]

class ApproximationDataImporter:
    def __init__(self, file_name, threshold=10):
        self.file_name = file_name
        self.threshold = threshold
        self.angle = []
        self.stiffness = []
        self.camera = []

    def import_from_csv(self):
        with open(self.file_name) as datafile:
            print(self.file_name)
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

        print(self.coeffs)

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

    def save_function(self):
        self.approximating_function = self.get_approximating_function()
        self.save_function_to_file(DEFAULT_FUNCTION)


#######################################################################################
    # # TODO move plotting functions somewhere else
    # def plot_approximating_function(self):
    #     x_range = np.linspace(min(self.angle), max(self.angle), 10)
    #     y_range = np.linspace(min(self.stiffness), max(self.stiffness), 10)
    #     X, Y = np.meshgrid(x_range, y_range)
    #
    #     Z = self.approximating_function(X, Y)
    #
    #     # plots 3D chart
    #     fig = plt.figure()
    #     ax = fig.gca(projection='3d')
    #
    #     ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.6)
    #     ax.scatter(self.angle, self.stiffness, self.camera, c='r', s=3)
    #
    #     plt.xlabel('servo angle')
    #     plt.ylabel('stiffness')
    #     ax.set_zlabel('camera angle')
    #
    #     plt.show()
    #     # plt.savefig('../data/interpolation_experiment.png')
    #
    # def plot_errors(self):
    #     predictions = self.approximating_function(self.angle, self.stiffness)
    #     errors = self.camera - predictions
    #
    #     # plots 3D chart
    #     fig = plt.figure()
    #     ax = fig.gca(projection='3d')
    #
    #     ax.scatter(self.angle, self.stiffness, errors, c='r', s=3)
    #
    #     plt.xlabel('servo angle')
    #     plt.ylabel('stiffness')
    #     ax.set_zlabel('prediction error')
    #
    #     plt.show()
    #
    # def plot_deviations_for_given_stiffness(self, bins_number):
    #     predictions = self.approximating_function(self.angle, self.stiffness)
    #     squared_errors = (self.camera - predictions) ** 2
    #
    #     variances = binned_statistic(self.stiffness, squared_errors, bins=bins_number)[0]
    #     deviations = np.sqrt(variances)
    #
    #     bin_range = np.linspace(min(self.stiffness), max(self.stiffness), bins_number+1)[:-1]
    #     plt.plot(bin_range, deviations)
    #     plt.show()


if __name__ == '__main__':
    path = get_default_file()
    importer = ApproximationDataImporter(path)
    importer.import_from_csv()
    finder = ApproximatingFunctionFinder(importer)
    print(finder.approximating_function)
