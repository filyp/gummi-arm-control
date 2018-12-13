from scipy.interpolate import interp1d


class LinearInterpolator:
    """Tells what angle we should send to servos, to move arm to given angle.

    It uses simple linear function to interpolate this value.

    Args:
        angle_relation:  see Configurator.turn_on_linear_interpolation

    """
    def __init__(self, angle_relation):
        servo_angles = list(angle_relation.keys())
        arm_angles = list(angle_relation.values())
        self.interpolation = interp1d(arm_angles,
                                      servo_angles,
                                      fill_value='extrapolate')

    def get_servo_angle(self, arm_angle):
        return self.interpolation(arm_angle)
