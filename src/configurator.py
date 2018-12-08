import json
import logging
import os

from src.constants import CONFIG_FILES, DEFAULT_CONFIG, DEFAULT_FUNCTION


class Configurator:
    """Save and load position control configuration."""

    def __init__(self):
        self.config = {}

    def load_config(self, filename=DEFAULT_CONFIG):
        """Loads position control configuration.

        Looks for given file inside config directory,
        specified in src.constants.

        Args:
            filename: name of the json file

        Raises:
            FileNotFoundError:  if there's no such file in config directory

        """
        absolute_filename = os.path.join(CONFIG_FILES, filename)
        with open(absolute_filename, 'r') as file:
            self.config = json.load(file)

    def save_config(self, filename=DEFAULT_CONFIG):
        """Saves configuration stored in this class to a file.

        It's saved as a human readable json,
        into a config directory specified in src.constants.

        Args:
            filename: name of the json file

        """
        absolute_filename = os.path.join(CONFIG_FILES, filename)
        with open(absolute_filename, 'w') as file:
            json.dump(self.config, file, indent=4)

    def turn_on_pid(self, P, I, D, interception_moment=1):
        self.config['PID'] = self._get_parameters(locals())

    def turn_on_approximating_function(self, filename=DEFAULT_FUNCTION):
        self.config['approximation'] = self._get_parameters(locals())

    def turn_on_naive_approximation(self, linear_map={0: 0, 180: 180}):
        """

        Args:
            linear_map:

        """
        self.config['approximation'] = self._get_parameters(locals())

    def turn_on_movement_control(self, max_servo_speed=250, stiffness_slope=0):
        """

        Args:
            max_servo_speed:    speed in degrees/second
            stiffness_slope:    float between 0 and 2,

        """
        self.config['movement_control'] = self._get_parameters(locals())
        # for movement control, some angle approximation is needed
        if 'approximation' not in self.config:
            self.turn_on_naive_approximation()

    def turn_off_pid(self):
        self._turn_off('PID')

    def turn_off_approximation(self):
        self._turn_off('approximation')

    def turn_off_movement_control(self):
        self._turn_off('movement_control')

    def _get_parameters(self, raw_parameters):
        """From given dict, cut out 'self' key."""
        return {key: val for key, val in raw_parameters.items()
                if key != 'self'}

    def _turn_off(self, attribute):
        """Turn off given attribute from config."""
        try:
            del self.config[attribute]
        except KeyError:
            logging.info(f'{attribute} is already turned off')
