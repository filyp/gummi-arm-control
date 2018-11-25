from src import maestro


class OutOfRangeError(ValueError):
    pass


class RawController:
    MAX_ANGLE = 180
    MIN_MAESTRO = 4 * 496
    MAX_MAESTRO = 4 * 2496
    # 496 and 2496 are min and max values set in
    # MaestroControlCenter -> Channel Settings
    BACK_SERVO = 0
    FRONT_SERVO = 1

    def __init__(self, servos_inverted=True):
        """Sends raw angle and stiffness commands to the arm.

        Note:
            Raw angle is the one that servos rotate to.
            It is not the angle that the whole arm will move to.

        Args:
            servos_inverted: if you attached tendons the wrong way,
                             just negate this value
        """
        self.maestro = maestro.Controller()
        self.servos_inverted = servos_inverted

    def get_back_angle(self, raw_angle, stiffness):
        """Compute angle that will be sent to servo on the back.

        If you attached servos or tendons the wrong way, just change signs
        in this function and in get_front_angle.

        Args:
            raw_angle:  Angle (in degrees) meant to change arm's position.
            stiffness:  Additional angle that each servo should rotate in opposite directions.
                        It's not meant to change arm's position, but rather tendon stiffness.

        Returns:
            Final angle that will be sent to servo.

        """
        if self.servos_inverted:
            return 180 - (raw_angle + stiffness)
        else:
            return raw_angle + stiffness

    def get_front_angle(self, raw_angle, stiffness):
        """Analogical to get_back_angle."""
        return raw_angle - stiffness

    def _angle_valid(self, angle):
        """Return if given angle is inside the servos range."""
        return 0 <= angle <= self.MAX_ANGLE

    def degrees_to_quarter_millis(self, angle_in_degrees):
        ratio = angle_in_degrees / self.MAX_ANGLE
        quarter_millis = self.MIN_MAESTRO + (self.MAX_MAESTRO - self.MIN_MAESTRO) * ratio
        return int(quarter_millis)

    def send(self, raw_angle, stiffness):
        """Send given position to the arm."""
        servo_back_angle = self.get_back_angle(raw_angle, stiffness)
        servo_front_angle = self.get_front_angle(raw_angle, stiffness)
        if self._angle_valid(servo_back_angle) and self._angle_valid(servo_front_angle):
            target1 = self.degrees_to_quarter_millis(servo_back_angle)
            target2 = self.degrees_to_quarter_millis(servo_front_angle)
            self.maestro.setTarget(self.BACK_SERVO, target1)
            self.maestro.setTarget(self.FRONT_SERVO, target2)
        else:
            raise OutOfRangeError
