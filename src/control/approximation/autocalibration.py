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
    # ask about custom duration of experiment
    try:
        duration = int(input("""Put experiment duration in seconds. Default is 2"""))
        print('Started data_for_approximation experiment with duration: %'.format(duration))
        approximation_experiment.start()
    except ValueError:
        print('Started data_for_approximation experiment with default iteration number')
        approximation_experiment.start()
        pass

    print("Experiment finished. Results in data dir")

    # drawing data_for_approximation data
    # ask about source data_for_approximation data file
    executor = None
    try:
        file_name = input("""For drawing put data .csv filename from data/approximation/data_for_approximation dir. 
        Default is the latest one""")

        # TODO change path
        if os.path.isfile('../data/data_for_approximation/' + file_name):
            executor = ApproximatingFunctionFinder(file_name)
        else:
            print('Used default data_for_approximation data .csv file')
            executor = ApproximatingFunctionFinder()
    except IOError:
        print('Cannot open file')
        pass
    # plotting and saving chart
    # TODO change to saving 3D chart automatically
    executor.plot_approximating_function()

except IOError:
    print('No camera found')
finally:
    position_detector.kill()
    position_detector.join()
