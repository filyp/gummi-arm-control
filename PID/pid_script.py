from PID.pid_controller import PIDController
from src.look import PositionDetector
from src.position_controller import PositionController

STIFFNESS = 10
TARGET_ANGLE = 90
STARTING_POSITION = 0

raw_controller = PositionController()
position_detector = PositionDetector(1.0)

pid_controller = PIDController(position_detector, raw_controller)
raw_controller.send(STARTING_POSITION, STIFFNESS)

pid_controller.control(TARGET_ANGLE, STARTING_POSITION, STIFFNESS)
