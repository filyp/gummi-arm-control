import sys
from ruamel.yaml import YAML
from src.benchmark import accuracy_experiment
from src.benchmark.test_utils.accuracy_stats import AccuracyStats

FILE_LOCATION = "../../../config/tests_config"

yaml = YAML(typ='safe')
my_dict = yaml.load(open(FILE_LOCATION))

if my_dict['accuracy_experiment'] is not None:
    print('Started examining data_for_approximation accuracy_experiment')
    accuracy_experiments = []
    current_experiment = my_dict['accuracy_experiment']
    for key in current_experiment:
        accuracy_experiment.start(current_experiment[key]['angle'], current_experiment[key]['stiffness'])
    accuracy_stats = AccuracyStats()
    accuracy_stats.generate_statistics()


if my_dict['dupa_experiment'] is not None:
    print('dupa')

