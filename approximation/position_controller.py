from approximation.servo_angle_interpolator import ServoAngleInterpolator
from src import raw_controller


class PositionController:
    # TODO add config file
    def __init__(self):
        self.interpolator = ServoAngleInterpolator()
        self.raw_controller = raw_controller.RawController()

    def send(self, angle, stiffness):
        servo_angle = self.interpolator.get_servo_angle(angle, stiffness)
        self.raw_controller.send(servo_angle, stiffness)
