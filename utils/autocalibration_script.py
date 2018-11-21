import os

from interpolation.interpolation import InterpolationExecutor
from src.look import PositionDetector
import experiments.interpolation_experiment as interpolation_experiment
import experiments.accuracy_experiment as accuracy_experiment
import utils.chart_drawer as accuracy_chart_drawer

print("welcome in  auto-calibration mode. Please, enjoy your arm!")
print("""Put camera in front of arm's glyphs and make sure that all four glyphs in max/min arm position are visible""")

position_detector = PositionDetector(1)
try:
    position_detector.connect_camera()
    print('Camera connected')
    position_detector.kill()
    position_detector.join()

    # interpolation experiment
    # ask about custom iteration number
    try:
        iteration_number = int(input("""If you want, put number of iterations of interpolation
        experiment. Default number is 400"""))
        print('Started interpolation experiment with iteration number: %'.format(iteration_number))
        interpolation_experiment.start(iteration_number=iteration_number)
    except ValueError:
        print('Started interpolation experiment with default iteration number')
        interpolation_experiment.start()
        pass

    print("Experiment finished. Results in data dir")

    # drawing interpolation data
    # ask about source interpolation data file
    executor = None
    try:
        file_name = input("""Put interpolation data .csv file name from data/interpolation dir. 
        Default is the latest one""")
        if os.path.isfile('../data/interpolation/' + file_name):
            executor = InterpolationExecutor(file_name)
        else:
            print('Used default interpolation data .csv file')
            executor = InterpolationExecutor()
    except IOError:
        print('Cannot open file')
        pass
    # plotting and saving chart
    executor.plot()
    # print("Result chart with interpolated surface in .... dir")

    # accuracy experiment
    try:
        configuration_string = input("""If you want, put array of tuples of accuracy test data 
        (examine_angle_1, (examine_stiffness_1, examine_stiffness_2)),
        (examine_angle_2, examine_stiffness_3, examine_stiffness_4). Default is (90, (0,3,5))""")
        # TODO pupa tutaj, sprawdzac pattern
        if configuration_string != '':
            accuracy_experiment.start(configuration_string=configuration_string)
        else:
            print('Started examining interpolation accuracy with default configuration')
            accuracy_experiment.start()
    except IOError:
        print('Error while getting configuration string')
        pass

    print("Experiment finished. Results in data dir")

    # drawing accuracy data
    accuracy_chart_drawer.start()
    print("Result charts with interpolated surface in .... dir")


except IOError:
    print('No camera found')
finally:
    position_detector.kill()
    position_detector.join()
