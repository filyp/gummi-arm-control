import scipy.optimize
import numpy as np


from interpolation.interpolation import InterpolationExecutor


class ServoAngleInterpolator:
    def __init__(self):
        executor = InterpolationExecutor()
        # executor.import_from_csv()
        self.f = executor.interpolate_2()

    def get_servo_angle(self, result_angle, stiffness):
        x_a = scipy.optimize.fsolve(lambda x: self.f(x, stiffness) - int(result_angle), np.array([0]))
        servo_angle = int(x_a[0])

        return servo_angle
