import os

from ruamel.yaml import YAML
from src.benchmark.accuracy_test import accuracy_experiment
from src.benchmark.accuracy_test.accuracy_stats import AccuracyStats
from src.constants import DEFAULT_TEST_CONFIG, DEFAULT_ARM_CONFIG, CONFIG_FILES


class TestConfigurationLoader:
    def __init__(self, file_name):
        self.file_name = file_name

    def load_test_configuration(self):
        yaml = YAML(typ='safe')
        config_dict = yaml.load(open(self.file_name))

        return config_dict


class TestExecutor:
    def __init__(self, file_name=DEFAULT_TEST_CONFIG):
        abs_file = os.path.join(CONFIG_FILES, file_name)
        self.config = TestConfigurationLoader(abs_file).load_test_configuration()

    def start(self, arm_config=DEFAULT_ARM_CONFIG):
        if self.config['accuracy_experiment']:
            print('Started examining data_for_approximation accuracy_experiment')
            experiment = self.config['accuracy_experiment']
            for _, item in experiment.items():
                accuracy_experiment.start(item['angle'],
                                          item['stiffness'],
                                          arm_config)
            accuracy_stats = AccuracyStats()
            accuracy_stats.generate_statistics()

        # you can add another test strategies here
        # if ... is not None:
