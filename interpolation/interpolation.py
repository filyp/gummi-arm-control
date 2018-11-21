import csv
import glob

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import scipy.linalg

LOCATION = '../data/interpolation/*'


def get_default_file(location):
    datafiles = glob.glob(location)
    if not datafiles:
        raise IOError('No datafiles found')
    return sorted(datafiles)[-1]


class InterpolationExecutor:
    def __init__(self, file_name=None):
        self.angle = []
        self.stiffness = []
        self.camera = []
        self.coeffs = None

        if not file_name:
            file_name = get_default_file(LOCATION)

        self.import_from_csv(file_name)

    def import_from_csv(self, file_name):
        with open(file_name) as datafile:
            print(file_name)
            input_data = csv.DictReader(datafile)

            for row in input_data:
                if row['camera'] == 'nan':
                    continue
                self.angle.append(int(row['angle']))
                self.stiffness.append(int(row['stiffness']))
                self.camera.append(float(row['camera']))
        self.filter_outliers(10)

    def get_approximating_function(self):
        # c_ method added items along second axis
        data = np.c_[self.angle, self.stiffness, self.camera]

        # Best-fit quadratic curve
        A = np.c_[np.ones(data.shape[0]), data[:, :2], np.prod(data[:, :2], axis=1), data[:, :2] ** 2]
        # Solve for a least squares estimate
        self.coeffs, _, _, _ = scipy.linalg.lstsq(A, data[:, 2])

        return lambda x, y: self.coeffs[4] * x ** 2. + \
                            self.coeffs[5] * y ** 2. + \
                            self.coeffs[3] * x * y + \
                            self.coeffs[1] * x + \
                            self.coeffs[2] * y + \
                            self.coeffs[0]

    def filter_outliers(self, threshold):
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

            if mahalanobis_deviation[0, 0] < threshold:
                filtered_values.append(data_tuple.tolist()[0])

        self.angle, self.stiffness, self.camera = np.transpose(filtered_values)

    def plot(self):
        x_range = np.linspace(min(self.angle), max(self.angle), 10)
        y_range = np.linspace(min(self.stiffness), max(self.stiffness), 10)
        X, Y = np.meshgrid(x_range, y_range)

        approximating_function = self.get_approximating_function()
        Z = approximating_function(X, Y)

        # plots 3D chart
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.6)
        ax.scatter(self.angle, self.stiffness, self.camera, c='r', marker='o')

        plt.xlabel('servo angle')
        plt.ylabel('stiffness')
        ax.set_zlabel('camera angle')

        plt.show()
        # plt.savefig('../data/interpolation_experiment.png')


if __name__ == '__main__':
    ie = InterpolationExecutor()
    ie.plot()

