import os


project_path = os.path.join(os.path.dirname(__file__), '../')


def get_absolute_path(path):
    return os.path.join(project_path, path)


CONFIG_FILES = get_absolute_path(
    'config/')
APPROXIMATING_FUNCTIONS_PATH = get_absolute_path(
    'data/functions/')
APPROXIMATION_DATA_PATH = get_absolute_path(
    'data/experiments_results/approximation_experiment/data/')
APPROXIMATION_RESULTS_PATH = get_absolute_path(
    'data/experiments_results/approximation_experiment/results/')
ACCURACY_DATA_PATH = get_absolute_path(
    'data/experiments_results/accuracy_experiment/data/')
ACCURACY_RESULTS_PATH = get_absolute_path(
    'data/experiments_results/accuracy_experiment/results/')

DEFAULT_FUNCTION = 'default.pickle'
DEFAULT_CONFIG = 'default.json'
