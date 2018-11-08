from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
import scipy.linalg
import csv


class InterpolationExecutor:
    def __init__(self):
        self.angle = []
        self.stiffness = []
        self.camera = []
        self.function = None

    def import_from_csv(self, file_path="../src/collected_data.csv"):
        input_file = csv.DictReader(open(file_path))

        for row in input_file:
            self.angle.append((3.1415 * int(row['angle'])) / 180)
            self.stiffness.append(int(row['stiffness']))
            self.camera.append(float(row['camera']))

    def interpolate(self):
        degree = 3

        # np.vander(input array, number of columns in the output)
        A_angle = np.vander(self.angle, degree)
        A_stiffness = np.vander(self.stiffness, degree)
        A = np.hstack((A_angle, A_stiffness))

        # Solve for a least squares estimate
        (coeffs, residuals, rank, sing_vals) = np.linalg.lstsq(A, self.camera)

        # Extract coefficients and create polynomials in x and y
        xcoeffs = coeffs[0:degree]
        ycoeffs = coeffs[degree:2 * degree]
        print(ycoeffs)

        fx = np.poly1d(xcoeffs)
        fy = np.poly1d(ycoeffs)

        self.function = fx
        Z = np.array([fx(a) + fy(s) for (a, s) in zip(self.angle, self.stiffness)])

        new_fx = lambda x: fx(x) + 0.9335
        return new_fx, Z

    def interpolate_2(self):
        # c_ method added items along second axis
        data = np.c_[self.angle, self.stiffness, self.camera]

        x_range = np.arange(0, 3.14, 0.25)
        y_range = np.arange(-60, 60, 20)
        X, Y = np.meshgrid(x_range, y_range)
        XX = X.flatten()
        YY = Y.flatten()
        #
        # best-fit quadratic curve
        A = np.c_[np.ones(data.shape[0]), data[:, :2], np.prod(data[:, :2], axis=1), data[:, :2] ** 2]
        C, _, _, _ = scipy.linalg.lstsq(A, data[:, 2])

        # evaluate it on a grid
        Z = C[4] * X ** 2. + C[5] * Y ** 2. + C[3] * X * Y + C[1] * X + C[2] * Y + C[0]

        return Z

    def plot(self, Z):
        # plots 3D chart
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.scatter(self.angle, self.stiffness, Z)
        ax.scatter(self.angle, self.stiffness, self.camera, c='r', marker='o')

        plt.xlabel('angle')
        plt.ylabel('stiffness')
        ax.set_zlabel('camera')

        plt.show()
