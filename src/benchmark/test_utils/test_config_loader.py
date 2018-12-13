import sys
from ruamel.yaml import YAML
from src.benchmark import accuracy_experiment
from src.benchmark.test_utils.accuracy_stats import AccuracyStats

# todo add to constants
FILE_LOCATION = "../../../config/tests_config"


class TestConfigurationLoader:
    def __init__(self, file_name):
        self.file_name = file_name

    def load_test_configuration(self):
        yaml = YAML(typ='safe')
        config_dict = yaml.load(open(self.file_name))

        return config_dict


class TestExecutor:
    def __init__(self, file_name=FILE_LOCATION):
        self.config = TestConfigurationLoader(file_name).load_test_configuration()

    def start(self):

        if self.config['accuracy_experiment'] is not None:
            print('Started examining data_for_approximation accuracy_experiment')
            current_experiment = self.config['accuracy_experiment']
            for _, experiment in current_experiment.items():
                accuracy_experiment.start(experiment['angle'], experiment['stiffness'])
            accuracy_stats = AccuracyStats()
            accuracy_stats.generate_statistics()

        # you can add another test strategies here
        # if ... is not None:
