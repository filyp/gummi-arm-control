import os

from calibration.approximation import ApproximatingFunctionFinder
from position_detection.position_detector import PositionDetector
import calibration.collect_data as interpolation_experiment
import benchmark.accuracy_experiment as accuracy_experiment
import benchmark.chart_drawer as accuracy_chart_drawer

# TODO change to only testing script, without auto calibration

print("welcome in  auto-calibration mode. Please, enjoy your arm!")
print("""Put camera in front of arm's glyphs and make sure that all four glyphs in max/min arm position are visible""")

position_detector = PositionDetector(1)
try:
    position_detector.connect_camera()
    print('Camera connected')
    position_detector.kill()
    position_detector.join()

    # approximation experiment
    # ask about custom iteration number
    try:
        iteration_number = int(input("""If you want, put number of iterations of approximation
        experiment. Default number is 400"""))
        print('Started approximation experiment with iteration number: %'.format(iteration_number))
        interpolation_experiment.start(iteration_number=iteration_number)
    except ValueError:
        print('Started approximation experiment with default iteration number')
        interpolation_experiment.start()
        pass

    print("Experiment finished. Results in data dir")

    # drawing approximation data
    # ask about source approximation data file
    executor = None
    try:
        file_name = input("""Put approximation data .csv file name from data/approximation dir. 
        Default is the latest one""")
        if os.path.isfile('../data/approximation/' + file_name):
            executor = ApproximatingFunctionFinder(file_name)
        else:
            print('Used default approximation data .csv file')
            executor = ApproximatingFunctionFinder()
    except IOError:
        print('Cannot open file')
        pass
    # plotting and saving chart
    executor.plot_approximating_function()
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
            print('Started examining approximation accuracy with default configuration')
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
