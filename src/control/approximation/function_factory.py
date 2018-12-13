from src.control.approximation.approximating_function_finder import ApproximatingFunctionFinder, \
    ApproximationDataImporter
from src.control.approximation.autocalibration import Autocalibration
from src.control.approximation.approximating_function_finder import get_latest_approximation_file
from src.constants import DEFAULT_FUNCTION, APPROXIMATING_FUNCTIONS_PATH, APPROXIMATION_DATA_PATH
import os
import logging


class FunctionFactory:
    """Handle all logic of finding approximating function."""

    def __init__(self):
        pass

    @classmethod
    def function_exists(cls, function_file):
        abs_name = os.path.join(APPROXIMATING_FUNCTIONS_PATH, function_file)
        return os.path.isfile(abs_name)

    @classmethod
    def generate_approx_function(cls, raw_controller, position_detector):
        # approx_data = os.path.join(APPROXIMATION_DATA_PATH, approx_data_file_name)
        approx_data = get_latest_approximation_file()
        if approx_data:
            print(f'What data do you want to use for approximation?'
                  '   latest      to use most recently collected data'
                  '   new         to collect new data'
                  '   <filename>  file inside {APPROXIMATION_DATA_PATH}'
                  '               that you want to use')
            while True:
                approx_option = input()
                if approx_option == 'latest':
                    approx_data = get_latest_approximation_file()
                    break
                elif approx_option == 'new':
                    autocalibration = Autocalibration(raw_controller, position_detector)
                    autocalibration.run()
                    approx_data = get_latest_approximation_file()
                    break
                elif cls.function_exists(approx_option):
                    approx_data = approx_option
                    break
                else:
                    print('Invalid option, try again.')
        else:
            logging.info('No data for approximation found, gathering data first...')
            autocalibration = Autocalibration(raw_controller, position_detector)
            autocalibration.run()
            approx_data = get_latest_approximation_file()

        logging.info('Calculating approximating function...')
        importer = ApproximationDataImporter(approx_data)
        importer.import_from_csv()
        finder = ApproximatingFunctionFinder(importer)
        finder.save_function_and_stats()

