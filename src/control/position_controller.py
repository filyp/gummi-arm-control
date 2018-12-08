from src.control.approximation.approximator import ServoAngleApproximator
from src.control.raw_controller import RawController


class PositionController:
    # TODO add config file
    def __init__(self):
        self.approximator = ServoAngleApproximator()
        self.raw_controller = RawController()

    def send(self, angle, stiffness):
        """

        Args:
            angle:      angle that you want the arm to move to
            stiffness:  how tense tendons should be

        Raises:
            OutOfRangeError:    if given command is out of servos' range

        """
        servo_angle = self.approximator.get_servo_angle(angle, stiffness)
        self.raw_controller.send(servo_angle, stiffness)
