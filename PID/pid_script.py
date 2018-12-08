from PID.pid_controller import PIDController
from src.look import PositionDetector
from src.position_controller import PositionController
from src.control import maestro
import numpy as np


STIFFNESS = 10
TARGET_ANGLE = 90
STIFFNESS_FUNCTION = lambda x: x**2 # stub function of stiffness course

maestro = maestro.Controller()
position_detector = PositionDetector(1.0)
raw_controller = PositionController()

starting_servo_position = raw_controller.get_servo_position()
starting_position = int(position_detector.get_angle())

direction = np.sign(TARGET_ANGLE - starting_position)
tick = 2

angle_grid = range(starting_position, TARGET_ANGLE + direction, tick * direction)
stiffness_grid = [STIFFNESS_FUNCTION(a) for a in angle_grid]

if direction == -1:
    stiffness_grid = reversed(stiffness_grid)

pid_controller = PIDController(position_detector, raw_controller)
pid_controller.control(TARGET_ANGLE, starting_servo_position, stiffness_grid, tick)
