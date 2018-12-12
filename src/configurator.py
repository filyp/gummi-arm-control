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
        """

        Args:
            P:
            I:
            D:
            interception_moment:

        Notes:
            Parameters passed to this method must be the same as
            passed to <PID controller>.__init__.

        """
        self.config['PID'] = self._get_parameters(locals())

    def turn_on_approximating_function(self, function_file=DEFAULT_FUNCTION):
        """Find servo angles using function from given file.

        File should contain pickled function:
        (servo angle, stiffness) -> arm angle
        We'll reverse it to find servo angle.
        See ServoAngleApproximator.get_servo_angle

        Args:
            function_file: .pickle file containing the function

        Notes:
            Parameters passed to this method must be the same as
            passed to ServoAngleApproximator.__init__.

        """
        self.config['approximation'] = self._get_parameters(locals())

    def turn_on_movement_control(self, max_servo_speed=250, stiffness_slope=1):
        """Specify how stiffness should change during movement.

        For detailed description see MovementController.__init__

        Notes:
            Parameters passed to this method must be the same as
            passed to MovementController.__init__.

        """
        self.config['movement_control'] = self._get_parameters(locals())
        # for movement control, some angle approximation is needed
        if 'approximation' not in self.config:
            self.turn_on_approximating_function()

    def set_camera_address(self, ip, port):
        """Set address of remote camera used for position detection.

        If none is set, built-in or USB camera will be used.

        """
        self.config['camera'] = self._get_parameters(locals())

    def turn_off_pid(self):
        self._turn_off('PID')

    def turn_off_approximation(self):
        self._turn_off('approximation')

    def turn_off_movement_control(self):
        self._turn_off('movement_control')

    def unset_camera(self):
        """If remote camera was set, unset it.

        After that, position detector will use built-in or USB camera.

        """
        self._turn_off('camera')

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
