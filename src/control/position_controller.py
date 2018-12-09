import logging
import textwrap

from src.configurator import Configurator
from src.control.approximation.approximator import ServoAngleApproximator
from src.control.movement_controller import MovementController
from src.control.raw_controller import RawController
from src.constants import DEFAULT_CONFIG


class PositionController:

    def __init__(self):
        self.raw_controller = RawController()
        self.configurator = Configurator()
        self.config = {}
        self.modules = None

        self.approximator = None
        self.movement = None
        self.pid = None
        self.camera = None

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
            self.approximator = ServoAngleApproximator(**approx_params)
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
            # self.pid = PIDControllerOrWhatever(**pid_params)
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
            raise NotImplementedError
        elif not self.modules:
            logging.error('to send, you must first load some configuration')
