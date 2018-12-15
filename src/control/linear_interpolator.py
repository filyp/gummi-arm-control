from scipy.interpolate import interp1d


class LinearInterpolator:
    """Tells what angle we should send to servos, to move arm to given angle.

    It uses simple linear function to interpolate this value.

    Args:
        See Configurator.turn_on_linear_interpolation

    """
    def __init__(self, servo1, arm1, servo2, arm2):
        self.interpolation = interp1d([arm1, arm2],
                                      [servo1, servo2],
                                      fill_value='extrapolate')

    def get_servo_angle(self, arm_angle):
        return self.interpolation(arm_angle)
