import csv
import datetime
import os  # os module imported here

import matplotlib.pyplot as plt
import numpy as np
import scipy.linalg

location = '../data/interpolation'


def get_default_file():
    latest_timestamp = None
    file_name = None

    for file in os.listdir(location):
        try:
            if file.endswith(".csv"):
                file_name, timestamp_string = file.split('_')
                t = datetime.datetime.strptime(timestamp_string, "%Y-%m-%d %H:%M:%S")

                if latest_timestamp is None:
                    latest_timestamp = t
                else:
                    latest_timestamp = max((latest_timestamp, t))

        except Exception as e:
            print("No files found here")
            raise e
    return file_name + latest_timestamp


class InterpolationExecutor:
    def __init__(self, file_name=get_default_file()):
        self.angle = []
        self.stiffness = []
        self.camera = []
        self.coeffs = None

        self.import_from_csv(file_name)

    def import_from_csv(self, file_name):
        file_path = location + '/' + file_name
        input_file = csv.DictReader(open(file_path))

        for row in input_file:
            self.angle.append(int(row['angle']))
            self.stiffness.append(int(row['stiffness']))
            self.camera.append(float(row['camera']))

    # def interpolate(self):
    #     degree = 3
    #
    #     # np.vander(input array, number of columns in the output)
    #     A_angle = np.vander(self.angle, degree)
    #     A_stiffness = np.vander(self.stiffness, degree)
    #     A = np.hstack((A_angle, A_stiffness))
    #
    #     # Solve for a least squares estimate
    #     (coeffs, residuals, rank, sing_vals) = np.linalg.lstsq(A, self.camera)
    #
    #     # Extract coefficients and create polynomials in x and y
    #     xcoeffs = coeffs[0:degree]
    #     ycoeffs = coeffs[degree:2 * degree]
    #     print(ycoeffs)
    #
    #     fx = np.poly1d(xcoeffs)
    #     fy = np.poly1d(ycoeffs)
    #
    #     self.function = fx
    #     Z = np.array([fx(a) + fy(s) for (a, s) in zip(self.angle, self.stiffness)])
    #
    #     new_fx = lambda x: fx(x) + 0.9335
    #     return new_fx, Z

    def interpolate_2(self):
        # c_ method added items along second axis
        data = np.c_[self.angle, self.stiffness, self.camera]

        # best-fit quadratic curve
        A = np.c_[np.ones(data.shape[0]), data[:, :2], np.prod(data[:, :2], axis=1), data[:, :2] ** 2]
        self.coeffs, _, _, _ = scipy.linalg.lstsq(A, data[:, 2])

        result_fxy = lambda x, y: self.coeffs[4] * x ** 2. + self.coeffs[5] * y ** 2. + self.coeffs[3] * x * y + self.coeffs[1] * x + self.coeffs[2] * y + self.coeffs[0]

        return result_fxy

    def plot(self):
        _ = self.interpolate_2()

        x_range = np.arange(0, 200, 20)
        y_range = np.arange(0, 6, 1)
        X, Y = np.meshgrid(x_range, y_range)

        # evaluate it on a grid
        Z = self.coeffs[4] * X ** 2. + self.coeffs[5] * Y ** 2. + self.coeffs[3] * X * Y + self.coeffs[1] * X + self.coeffs[2] * Y + self.coeffs[0]

        # plots 3D chart
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.6)
        # ax.scatter(self.angle, self.stiffness, Z)
        ax.scatter(self.angle, self.stiffness, self.camera, c='r', marker='o')

        plt.xlabel('servo angle')
        plt.ylabel('stiffness')
        ax.set_zlabel('camera angle')

        plt.show()

# executor = InterpolationExecutor()
# executor.import_from_csv()
# Z = executor.interpolate_2()
# executor.plot(Z)
