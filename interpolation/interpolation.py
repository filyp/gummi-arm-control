import csv
import glob

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import scipy.linalg

location = '../data/interpolation/*'


def get_default_file():
    datafiles = glob.glob(location)
    if not datafiles:
        raise IOError('No datafiles found')
    return sorted(datafiles)[-1]

    # latest_timestamp = None
    # file_name = None
    #
    # for file in os.listdir(location):
    #     try:
    #         if file.endswith(".csv"):
    #             file_name, timestamp_string = file.split('_')
    #             timestamp_string = timestamp_string.replace('.csv', '')
    #             print(timestamp_string)
    #             t = datetime.datetime.strptime(timestamp_string, "%Y-%m-%d %H:%M:%S")
    #
    #             if latest_timestamp is None:
    #                 latest_timestamp = t
    #             else:
    #                 latest_timestamp = max((latest_timestamp, t))
    #
    #     except Exception as e:
    #         print("No files found here")
    #         raise e
    # return '{}_{}.csv'.format(file_name, latest_timestamp.strftime("%Y-%m-%d %H:%M:%S"))


class InterpolationExecutor:
    def __init__(self, file_name=get_default_file()):
        self.angle = []
        self.stiffness = []
        self.camera = []
        self.coeffs = None

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

    def plot(self):
        x_range = np.linspace(min(self.angle), max(self.angle), 50)
        y_range = np.linspace(min(self.stiffness), max(self.stiffness), 50)
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

