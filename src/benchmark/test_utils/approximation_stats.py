import matplotlib.pyplot as plt
import numpy as np
import scipy.linalg
from scipy.stats import binned_statistic
from mpl_toolkits.mplot3d import Axes3D

from src.constants import APPROXIMATION_RESULTS_PATH


class ApproximationStat:
    def __init__(self, finder):
        self.approximating_function = finder.approximating_function
        self.angle = finder.importer.angle
        self.stiffness = finder.importer.stiffness
        self.camera = finder.importer.camera

    def plot_approximating_function(self):
        x_range = np.linspace(min(self.angle), max(self.angle), 10)
        y_range = np.linspace(min(self.stiffness), max(self.stiffness), 10)
        X, Y = np.meshgrid(x_range, y_range)

        Z = self.approximating_function(X, Y)

        # plots 3D chart
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.6)
        ax.scatter(self.angle, self.stiffness, self.camera, c='r', s=3)

        plt.xlabel('servo angle')
        plt.ylabel('stiffness')
        ax.set_zlabel('camera angle')

        plt.show()
        # plt.savefig('../data/interpolation_experiment.png')

    def plot_errors(self):
        predictions = self.approximating_function(self.angle, self.stiffness)
        errors = self.camera - predictions

        # plots 3D chart
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        ax.scatter(self.angle, self.stiffness, errors, c='r', s=3)

        plt.xlabel('servo angle')
        plt.ylabel('stiffness')
        ax.set_zlabel('prediction error')

        plt.show()

    def plot_deviations_for_given_stiffness(self, bins_number):
        predictions = self.approximating_function(self.angle, self.stiffness)
        squared_errors = (self.camera - predictions) ** 2

        variances = binned_statistic(self.stiffness, squared_errors, bins=bins_number)[0]
        deviations = np.sqrt(variances)

        bin_range = np.linspace(min(self.stiffness), max(self.stiffness), bins_number+1)[:-1]
        plt.plot(bin_range, deviations)
        plt.savefig('{}deviations_stiffness_{}.png'.format(APPROXIMATION_RESULTS_PATH, bins_number))
