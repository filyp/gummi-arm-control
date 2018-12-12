import os


project_path = os.path.join(os.path.dirname(__file__), '../')

approximating_functions = 'data/functions/'

approximation_data = 'data/experiments_results/approximation_experiment/data/'
approximation_results = 'data/experiments_results/approximation_experiment/results/'

accuracy_data = 'data/experiments_results/accuracy_experiment/data/'
accuracy_results = 'data/experiments_results/accuracy_experiment/results/'
accuracy_data_files_list = 'data/experiments_results/accuracy_experiment/data/*'

config_files = 'config/'


def get_absolute_path(path):
    return os.path.join(project_path, path)


APPROXIMATING_FUNCTIONS_PATH = get_absolute_path(approximating_functions)

APPROXIMATION_DATA_PATH = get_absolute_path(approximation_data)
APPROXIMATION_RESULTS_PATH = get_absolute_path(approximation_results)

ACCURACY_DATA_PATH = get_absolute_path(accuracy_data)
ACCURACY_RESULTS_PATH = get_absolute_path(accuracy_results)
ACCURACY_FILES_LIST_PATH = get_absolute_path(accuracy_data_files_list)

DEFAULT_FUNCTION = 'default.pickle'
CONFIG_FILES = get_absolute_path(config_files)
DEFAULT_CONFIG = 'default.json'
