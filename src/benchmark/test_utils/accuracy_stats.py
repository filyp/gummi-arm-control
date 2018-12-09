import csv
import matplotlib.pyplot as plt
import numpy as np
import glob

import os  # os module imported here

location = '../../../../data/approximation/validation/*'


class OneExperimentStats:
    def __init__(self, file_name, stats_file_name):
        self.MARGIN_Y = 2
        self.MARGIN_X = 10
        self.prev_angle, self.angle, self.stiffness, self.baseline_value = self.load_data(file_name)
        self.stats_file_name = stats_file_name

    def load_data(self, file_name):
        input_file = csv.DictReader(open(location[:-1] + file_name))

        prev_angle = []
        angle = []
        stiffness = None
        examine_angle = None

        for row in input_file:
            angle.append(float(row['angle']))
            prev_angle.append(float(row['prev_angle']))
            stiffness = int(row['stiffness'])
            examine_angle = int(row['examine_angle'])
        return prev_angle, angle, stiffness, examine_angle

    def save_chart(self):
        baseline = np.arange(min(self.prev_angle) - self.MARGIN_X, max(self.prev_angle) + self.MARGIN_X)
        plt.plot(baseline, np.ones_like(baseline) * self.baseline_value, self.prev_angle, self.angle, 'ro')
        plt.yticks(range(self.baseline_value - self.MARGIN_Y, self.baseline_value + self.MARGIN_Y))
        plt.title("Examine angle: {} Stiffness: {}".format(self.baseline_value, self.stiffness))
        plt.xlabel('starting position (deg)')
        plt.ylabel('ending position (deg)')
        plt.savefig('accuracy_experiment' + str(self.baseline_value) + str(self.stiffness) + '.png')

    def save_statistics(self):
        mean = np.mean(self.angle)
        median = np.median(self.angle)
        std = np.std(self.angle)

        row = [self.baseline_value, self.stiffness, mean, median, std]

        with open(self.stats_file_name, 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(row)


class AccuracyStats:
    def create_files_list(self):
        datafiles = glob.glob(location)
        return datafiles

    def generate_statistics(self):
        files_list = self.create_files_list()
        stats_file_name = "accuracy_experiment_statistics"

        row = ['examine_angle', 'stiffness', 'mean', 'median', 'std']

        with open(stats_file_name, 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        for file in files_list:
            one_stat = OneExperimentStats(file, stats_file_name)
            one_stat.save_chart()
            one_stat.save_statistics()

