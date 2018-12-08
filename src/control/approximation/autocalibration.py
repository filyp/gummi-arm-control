import os

from src.control.approximation.approximating_function_finder import ApproximatingFunctionFinder
from src.position_detection.position_detector import PositionDetector
import src.benchmark.collect_data_for_approximation as interpolation_experiment


print("welcome in  auto-calibration mode. Please, enjoy your arm!")
print("""Put camera in front of arm's glyphs and make sure that all four glyphs in max/min arm position are visible""")

position_detector = PositionDetector(1)
try:
    position_detector.connect_camera()
    print('Camera connected')
    position_detector.kill()
    position_detector.join()

    # data_for_approximation experiment
    # ask about custom iteration number
    try:
        iteration_number = int(input("""If you want, put number of iterations of data_for_approximation
        experiment. Default number is 400"""))
        print('Started data_for_approximation experiment with iteration number: %'.format(iteration_number))
        interpolation_experiment.start(iteration_number=iteration_number)
    except ValueError:
        print('Started data_for_approximation experiment with default iteration number')
        interpolation_experiment.start()
        pass

    print("Experiment finished. Results in data dir")

    # drawing data_for_approximation data
    # ask about source data_for_approximation data file
    executor = None
    try:
        file_name = input("""Put data_for_approximation data .csv file name from data/data_for_approximation dir. 
        Default is the latest one""")
        if os.path.isfile('../data/data_for_approximation/' + file_name):
            executor = ApproximatingFunctionFinder(file_name)
        else:
            print('Used default data_for_approximation data .csv file')
            executor = ApproximatingFunctionFinder()
    except IOError:
        print('Cannot open file')
        pass
    # plotting and saving chart
    executor.plot_approximating_function()

except IOError:
    print('No camera found')
finally:
    position_detector.kill()
    position_detector.join()
