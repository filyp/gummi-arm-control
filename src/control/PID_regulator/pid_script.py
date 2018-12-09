from src.control.PID_regulator.pid_controller import PIDController
from src.position_detection.position_detector import PositionDetector
from src.control.raw_controller import RawController
from src.control import maestro
import numpy as np


STIFFNESS = 10
TARGET_ANGLE = 90
STIFFNESS_FUNCTION = lambda x: x**2 # stub function of stiffness course

position_detector = PositionDetector(1.0)
raw_controller = RawController()

starting_servo_position = raw_controller.get_servo_position()
starting_position = int(position_detector.get_angle())

# direction = np.sign(TARGET_ANGLE - starting_position)
# tick = 2
#
# angle_grid = range(starting_position, TARGET_ANGLE + direction, tick * direction)
# stiffness_grid = [STIFFNESS_FUNCTION(a) for a in angle_grid]
#
# if direction == -1:
#     stiffness_grid = reversed(stiffness_grid)

pid_controller = PIDController(position_detector, raw_controller, STIFFNESS_FUNCTION)
pid_controller.control(TARGET_ANGLE, starting_servo_position, STIFFNESS, starting_position)
