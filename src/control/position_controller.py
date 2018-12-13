import logging
import textwrap
from time import sleep

from src.configurator import Configurator
from src.control.PID_regulator.pid_controller import PIDController
from src.control.approximation.approximator import ServoAngleApproximator
from src.control.raw_controller import RawController
from src.constants import DEFAULT_CONFIG, DEFAULT_FUNCTION
from src.position_detection.position_detector import PositionDetector
from src.control.approximation.function_factory import FunctionFactory


class PositionController:
    possible_modules = {'approximation', 'PID'}

    def __init__(self):
        self.raw_controller = RawController()
        sleep(2)
        self.position_detector = None
        self.configurator = Configurator()
        self.config = {}
        self.modules = None

        self.approximator = None
        self.movement = None
        self.pid = None

    def load_config(self, filename=DEFAULT_CONFIG):
        """Load arm configuration from a file.

        For details on what can be configured see src.configurator.

        Args:
            filename: name of the config file inside directory specified in src.constants

        Notes:
            If camera is already connected, this method will use the existing one instead
            of connecting to the one in config. To reconnect you have to manually call:
            PositionController.connect_camera(reconnect_if_exists=True)

        """

        error_str = textwrap.dedent("""
            Invalid configuration file!
            
            Given modules:
                {}
            
            Possible combinations:
                approximation
                approximation + PID
                PID
        """)

        self.configurator.load_config(filename)
        self.config = self.configurator.config
        self.modules = self.config.keys() & self.possible_modules

        # unset previous values
        self.approximator = None
        self.movement = None
        self.pid = None

        # connect camera in case it will be needed for tests
        self.connect_camera()

        if self.modules == {'approximation'}:
            self._load_approximation_module()
        elif self.modules == {'approximation', 'PID'}:
            self._load_approximation_module()
            self._load_pid_module()
        elif self.modules == {'PID'}:
            self._load_pid_module()
        else:
            logging.error(error_str.format(self.modules))

    def _load_approximation_module(self):
        approx_params = self.config['approximation']
        function_file = approx_params['function_file']

        self.approximator = ServoAngleApproximator()

        if FunctionFactory.function_exists(function_file):
            self.approximator.load_approx_function(function_file)
            return
        elif FunctionFactory.function_exists(DEFAULT_FUNCTION):
            logging.warning(f'No {function_file} found, using {DEFAULT_FUNCTION} instead')
            self.approximator.load_approx_function(DEFAULT_FUNCTION)
            return
        logging.warning(
            f'No {function_file} or {DEFAULT_FUNCTION}found. Creating new function...')
        FunctionFactory.generate_approx_function(self.raw_controller, self.position_detector)
        self.approximator.load_approx_function(DEFAULT_FUNCTION)

    def _load_pid_module(self):
        # self.connect_camera()
        pid_params = self.config['PID']
        def stiffness_function(x):
            return x**2
        self.pid = PIDController(self.position_detector,
                                 self.raw_controller,
                                 stiffness_function,
                                 **pid_params)

    def connect_camera(self, reconnect_if_exists=False):
        """Connect to a camera specified in config.

        If no camera was specified in config, it will connect to
        built-in or USB camera.
        If this method was already called before, on default nothing happens.
        You can change that behavior by setting reconnect_if_exists,
        which will force reconnect.

        """
        if self.position_detector:
            if reconnect_if_exists:
                self.position_detector.kill()
                self.position_detector.join()
            else:
                return

        if 'camera' in self.config:
            camera_address = self.config['camera']
        else:
            camera_address = {}

        self.position_detector = PositionDetector(**camera_address)
        self.position_detector.start()

    def send(self, angle, stiffness):
        """Send given command to the arm.

        Moves according to parameters passed in config.

        Args:
            angle:      angle that you want the arm to move to
            stiffness:  how tense tendons should be

        Raises:
            OutOfRangeError:    if given command is out of servos' range

        """
        if self.modules == {'approximation'}:
            servo_angle = self.approximator.get_servo_angle(angle, stiffness)
            self.raw_controller.send(servo_angle, stiffness)
        elif self.modules == {'approximation', 'PID'}:
            starting_servo_position = self.raw_controller.get_servo_position()
            starting_arm_position = int(self.position_detector.get_angle())

            servo_angle = self.approximator.get_servo_angle(angle, stiffness)
            self.raw_controller.send(servo_angle, stiffness)
            self.pid.wait_for_interception(starting_arm_position, angle)
            self.pid.control(angle, starting_servo_position,
                             stiffness, starting_arm_position)

        elif self.modules == {'PID'}:
            starting_servo_position = self.raw_controller.get_servo_position()
            starting_arm_position = int(self.position_detector.get_angle())
            self.pid.control(angle, starting_servo_position,
                             stiffness, starting_arm_position)
        elif not self.modules:
            logging.error('To send, you must first load some configuration.')
