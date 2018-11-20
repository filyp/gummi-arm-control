from interpolation.servo_angle_interpolator import ServoAngleInterpolator
from src import position_controller


class InterpolationPositionController:
    def __init__(self):
        self.interpolator = ServoAngleInterpolator()
        self.controller = position_controller.PositionController()

    def send(self, angle, stiffness):
        servo_angle = self.interpolator.get_servo_angle(angle, stiffness)

        while True:
            try:
                self.controller.send(servo_angle, stiffness)
                break
            except ValueError:
                # chosen values were out of servos' range, so choose once again
                pass

        return servo_angle
