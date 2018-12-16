import ast
import csv
import time
import matplotlib.pyplot as plt


from src.constants import ACCURACY_DATA_PATH
from src.control.raw_controller import RawController
from src.position_detection.position_detector import PositionDetector

MAX_ANGLE = 180
# na movement_control lepiej widac oscylacje, na mc2 smieszniej jest. O
FILENAME_BASE = ACCURACY_DATA_PATH + 'movement_course'
DELAY = 4

# TODO merge this with accuracy_experiment.py because a lot is duplicated


def save_row(filename, row):
    """Append row to given .csv file.

    Args:
        filename: .csv file
        row: list of values

    """
    with open(filename, 'a+') as data:
        writer = csv.writer(data)
        writer.writerow(row)


def start(angle, stiffness):

    position_controller = RawController()
    position_detector = PositionDetector(1)
    position_detector.start()

    time.sleep(2)

    try:
        filename = '{}.csv'.format(FILENAME_BASE)
        labels = ["current_position", "time"]
        save_row(filename, labels)
        position_controller.send(60, stiffness)

        time.sleep(2)

        i = 0
        position_controller.send(angle, stiffness)
        while i < 50:
            current_position = position_detector.get_angle()
            curr_time = i
            row = [current_position, curr_time]
            save_row(filename, row)
            i+=0.05
    except KeyboardInterrupt:
        pass
    finally:
        position_detector.kill()
        position_detector.join()


def import_and_plot():
    with open(FILENAME_BASE + '.csv') as datafile:
        input_data = csv.DictReader(datafile)
        position = []
        curr_time = []

        for row in input_data:
            position.append(float(row['current_position']))
            curr_time.append(float(row['time']))

    plt.plot(curr_time, position)
    plt.show()


if __name__ == "__main__":
    # start(140, 0)
    import_and_plot()
