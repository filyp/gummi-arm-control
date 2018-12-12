from scipy.interpolate import interp1d


class LinearInterpolator:
    def __init__(self, angle_relation={0: 120, 12: 150}):
        arm_angles = list(angle_relation.keys())
        servo_angles = list(angle_relation.values())
        self.interpolation = interp1d(arm_angles,
                                      servo_angles,
                                      fill_value='extrapolate')

    def get_servo_angle(self, arm_angle):
        return self.interpolation(arm_angle)
