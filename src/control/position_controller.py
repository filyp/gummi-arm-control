import logging
import textwrap

from src.configurator import Configurator
from src.control.PID_regulator.pid_controller import PIDController
from src.control.approximation.approximator import ServoAngleApproximator
from src.control.movement_controller import MovementController
from src.control.raw_controller import RawController
from src.constants import DEFAULT_CONFIG
from src.position_detection.position_detector import PositionDetector


class PositionController:

    def __init__(self):
        self.raw_controller = RawController()
        # self.raw_controller = None
        # todo added handling custom camera in position detector HERE!
        self.position_detector = PositionDetector(1)
        # self.position_detector = None
        self.configurator = Configurator()
        self.config = {}
        self.modules = None

        self.approximator = None
        self.movement = None
        self.pid = None
        self.camera = None

        # starting position detector thread
        self.position_detector.start()

    def load_config(self, filename=DEFAULT_CONFIG):
        """

        Args:
            filename:

        """

        error_str = textwrap.dedent("""
            Invalid configuration file!
            
            Given modules:
                {}
            
            Possible combinations:
                approximation
                approximation + movement_control
                approximation + movement_control + PID
                PID
        """)

        self.configurator.load_config(filename)
        self.config = self.configurator.config
        self.modules = set(self.config.keys())

        self.approximator = None
        self.movement = None
        self.pid = None

        if self.modules == {'approximation'}:
            approx_params = self.config['approximation']
            self.approximator = ServoAngleApproximator(self.raw_controller, self.position_detector)
            self.approximator.load_or_generate_approx_function(**approx_params)
        elif self.modules == {'approximation', 'movement_control'}:
            approx_params = self.config['approximation']
            movement_params = self.config['movement_control']
            self.approximator = ServoAngleApproximator(**approx_params)
            self.movement = MovementController(**movement_params)
        elif self.modules == {'approximation', 'movement_control', 'PID'}:
            approx_params = self.config['approximation']
            movement_params = self.config['movement_control']
            pid_params = self.config['PID']
            self.approximator = ServoAngleApproximator(**approx_params)
            self.movement = MovementController(**movement_params)
            # self.pid = PIDControllerOrWhatever(**pid_params)
        elif self.modules == {'PID'}:
            pid_params = self.config['PID']

            # in pid_params: stiffness_function, P, I, D coeffs
            self.pid = PIDController(self.position_detector, self.raw_controller, **pid_params)
        else:
            logging.error(error_str.format(self.modules))

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
        elif self.modules == {'approximation', 'movement_control'}:
            servo_angle = self.approximator.get_servo_angle(angle, stiffness)
            self.movement.set_target(servo_angle, stiffness)
            while self.movement.completion != 1:
                intermediate_command = self.movement.get_command()
                self.raw_controller.send(*intermediate_command)
        elif self.modules == {'approximation', 'movement_control', 'PID'}:
            raise NotImplementedError
        elif self.modules == {'PID'}:
            starting_servo_position = self.raw_controller.get_servo_position()
            starting_position = int(self.position_detector.get_angle())
            self.pid.control(angle, starting_servo_position, stiffness, starting_position)
        elif not self.modules:
            logging.error('to send, you must first load some configuration')
