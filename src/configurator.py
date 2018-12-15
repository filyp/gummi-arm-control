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
            filename (str): name of the json file

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
            filename (str): name of the json file

        """
        absolute_filename = os.path.join(CONFIG_FILES, filename)
        with open(absolute_filename, 'w') as file:
            json.dump(self.config, file, indent=4)

    def enable_pid(self, P, I, D, interception_moment=1,
                   stiffness_function_string='lambda x: x'):
        """Enable PID control.

        Args:
            P, I, D (float): PID parameters
            interception_moment (float): ratio of completed movement,
                after which PID is turned on,
                for details see PIDController.wait_for_interception
            stiffness_function_string (str): contains lambda expression
                that will be used to control stiffness during movement,
                for details see PIDController.control

        Notes:
            Parameters passed to this method must correspond to those
            passed to PIDController.__init__.

        """
        self.config['PID'] = self._get_parameters(locals())

    def enable_approximating_function(self, function_file=DEFAULT_FUNCTION):
        """Find servo angles using function from given file.

        File should contain pickled function:
        (servo angle, stiffness) -> arm angle
        We'll reverse it to find servo angle.
        See ServoAngleApproximator.get_servo_angle

        Args:
            function_file (str): .pickle file containing the function

        Notes:
            Parameters passed to this method must correspond to those
            passed to ServoAngleApproximator.__init__.

        """
        self.config['approximation'] = self._get_parameters(locals())

    def enable_movement_control(self, max_servo_speed=250, stiffness_slope=1):
        """Specify how stiffness should change during movement.

        For detailed description see MovementController.__init__

        Notes:
            Parameters passed to this method must correspond to those
            passed to MovementController.__init__.

        """
        self.config['movement_control'] = self._get_parameters(locals())
        # for movement control, some angle approximation is needed
        if 'approximation' not in self.config:
            self.enable_approximating_function()

    def enable_linear_interpolation(self, angle_relation):
        """Find servo angles using linear interpolation.

        It requires sending two angles to servos using RawController
        and manually measuring what angle is reached by the arm for them.
        Then, pass these values as a dictionary.

        Args:
            angle_relation (dict): tells how servo angles relate to arm angles
                {servo_angle1: corresponding_arm_angle1,
                 servo_angle2: corresponding_arm_angle2}

        Notes:
            Make sure servo angles that you choose, are inside the range
            of arm's normal operation. Otherwise, interpolation will be skewed.

            Parameters passed to this method must correspond to those
            passed to LinearInterpolator.__init__.

        """
        self.config['linear_interpolator'] = self._get_parameters(locals())

    def set_camera_address(self, ip, port):
        """Set address of remote camera used for position detection.

        If none is set, built-in or USB camera will be used.

        """
        self.config['camera'] = self._get_parameters(locals())

    def disable_pid(self):
        self._disable('PID')

    def disable_approximation(self):
        self._disable('approximation')

    def disable_movement_control(self):
        self._disable('movement_control')

    def disable_linear_interpolation(self):
        self._disable('linear_interpolator')

    def unset_camera(self):
        """If remote camera was set, unset it.

        After that, position detector will use built-in or USB camera.

        """
        self._disable('camera')

    def _get_parameters(self, raw_parameters):
        """From given dict, cut out 'self' key."""
        return {key: val for key, val in raw_parameters.items()
                if key != 'self'}

    def _disable(self, attribute):
        """Disable given attribute from config."""
        try:
            del self.config[attribute]
        except KeyError:
            logging.info(f'{attribute} is already turned off')
