import textwrap

from src import maestro


class PositionController:
    """
    Connect by serial
    Set position and stiffness
    Send them to servos
    """
    MAX_ANGLE = 180
    MIN_MAESTRO = 4 * 496
    MAX_MAESTRO = 4 * 2496
    # 496 and 2496 are min and max values set in
    # MaestroControlCenter -> Channel Settings
    BACK_SERVO = 0
    FRONT_SERVO = 1

    def __init__(self):
        self.maestro = maestro.Controller()

    def get_back_angle(self, angle, stiffness):
        """Compute angle that will be sent to servo on the back.

        If you attached servos or tendons the wrong way, just change signs
        in this function and in get_front_angle.

        Args:
            angle:      Angle (in degrees) meant to change arm's position.
            stiffness:  Additional angle that each servo should rotate in opposite directions.
                        It's not meant to change arm's position, but rather tendon stiffness.

        Returns:
            Final angle that will be sent to servo.

        """
        return (180 - angle) - stiffness

    def get_front_angle(self, angle, stiffness):
        """Analogical to get_back_angle."""
        return angle - stiffness

    def _angle_valid(self, angle):
        """Return if given angle is inside the servos range."""
        return 0 <= angle <= self.MAX_ANGLE

    def degrees_to_quarter_millis(self, angle_in_degrees):
        ratio = angle_in_degrees / self.MAX_ANGLE
        quarter_millis = self.MIN_MAESTRO + (self.MAX_MAESTRO - self.MIN_MAESTRO) * ratio
        return int(quarter_millis)

    def send(self, arm_angle, stiffness):
        """Send given position to the arm."""
        angle1 = self.get_back_angle(arm_angle, stiffness)
        angle2 = self.get_front_angle(arm_angle, stiffness)
        if self._angle_valid(angle1) and self._angle_valid(angle2):
            target1 = self.degrees_to_quarter_millis(angle1)
            target2 = self.degrees_to_quarter_millis(angle2)
            self.maestro.setTarget(self.BACK_SERVO, target1)
            self.maestro.setTarget(self.FRONT_SERVO, target2)
        else:
            raise ValueError('servo command out of range')


def manual_control():
    """Function for manually controlling arm from command line."""

    controller = PositionController()
    help_string = f"""
    Type commands that will be sent to the arm.
    
    command: "<angle> <stiffness>"
    for example: "120 10"
    
    Angles in range <0, {controller.MAX_ANGLE}>
    For stiffness try out values for yourself.
    """
    print(textwrap.dedent(help_string))

    while True:
        angle_str, stiffness_str = input().split()
        angle, stiffness = int(angle_str), int(stiffness_str)
        try:
            controller.send(angle, stiffness)
        except ValueError as e:
            print(e)


if __name__ == '__main__':
    manual_control()
