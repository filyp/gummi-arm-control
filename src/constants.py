import os


project_path = os.path.join(os.path.dirname(__file__), '../')

data_for_approximation = 'data/data_for_approximation/*'
approximating_functions = 'data/functions/'
config_files = 'config/'


def get_absolute_path(path):
    return os.path.join(project_path, path)


DATA_FOR_APPROXIMATION = get_absolute_path(data_for_approximation)
APPROXIMATING_FUNCTIONS = get_absolute_path(approximating_functions)
DEFAULT_FUNCTION = 'default.pickle'
CONFIG_FILES = get_absolute_path(config_files)
DEFAULT_CONFIG = 'default.json'
