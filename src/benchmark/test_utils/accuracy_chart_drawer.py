import csv
import matplotlib.pyplot as plt
import numpy as np
import os  # os module imported here

location = '../data/validation'


def create_files_list():
    counter = 0  # keep a count of all files found
    csv_files = []  # list to store all csv files found at location

    for file in os.listdir(location):
        try:
            if file.endswith(".csv"):
                print("csv file found:\t", file)
                csv_files.append(str(file))
                counter = counter + 1
        except Exception as e:
            print("No files found here!")
            raise e

    print("Total files found:\t", counter)
    return csv_files


def generate_accuracy_chart(file_name, baseline_value, index):
    input_file = csv.DictReader(open(location + '/' + file_name))

    prev_angle = []
    angle = []
    stiffness = None

    for row in input_file:
        angle.append(float(row['angle']))
        prev_angle.append(float(row['prev_angle']))
        stiffness = int(row['stiffness'])

    baseline = np.arange(70, 140)

    print(index)
    plt.figure(index + 1)  # to let the index start at 1
    plt.plot(baseline, np.ones_like(baseline) * baseline_value, prev_angle, angle, 'ro')
    plt.yticks(range(88, 93))
    plt.title("Examine angle: {} Stiffness: {}".format(baseline_value, stiffness))
    plt.xlabel('starting position (deg)')
    plt.ylabel('ending position (deg)')
    plt.savefig('accuracy_experiment' + str(index) + '.png')


def start():
    files_list = create_files_list()
    current_baseline_value = 90

    for file in files_list:
        generate_accuracy_chart(file, current_baseline_value, files_list.index(file))
    # plt.show()


if __name__ == "__main__":
    start()
