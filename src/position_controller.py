import maestro


class PositionController:
    """
    Connect by serial
    Set position and stiffness
    Send them to servos
    """
    MAX_ANGLE = 180
    MIN_MAESTRO = 4000
    MAX_MAESTRO = 8000
    SERVO1 = 0
    SERVO2 = 1

    def __init__(self):
        self.maestro = maestro.Controller()

    def get_angle1(self, angle, stiffness):
        return angle - stiffness

    def get_angle2(self, angle, stiffness):
        return angle + stiffness

    def _angle_valid(self, angle):
        """return if given angle is inside the servos range"""
        return 0 <= angle <= self.MAX_ANGLE

    def degrees_to_quarter_millis(self, angle_in_degrees):
        ratio = angle_in_degrees / self.MAX_ANGLE
        quarter_millis = self.MIN_MAESTRO + (self.MAX_MAESTRO - self.MIN_MAESTRO) * ratio
        return int(quarter_millis)

    def send(self, arm_angle, stiffness):
        """send given position to the arm"""
        angle1 = self.get_angle1(arm_angle, stiffness)
        angle2 = self.get_angle2(arm_angle, stiffness)
        if self._angle_valid(angle1) and self._angle_valid(angle2):
            target1 = self.degrees_to_quarter_millis(angle1)
            target2 = self.degrees_to_quarter_millis(angle2)
            self.maestro.setTarget(self.SERVO1, target1)
            self.maestro.setTarget(self.SERVO2, target2)
        else:
            raise ValueError
