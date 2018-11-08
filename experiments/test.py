import time
from src import maestro
from config.constants import PORT, BAUDRATE


def degrees_to_quarter_millis(angle_in_degrees):
    MAX_ANGLE = 180
    MIN_MAESTRO = 4000
    MAX_MAESTRO = 8000
    ratio = angle_in_degrees / MAX_ANGLE
    quarter_millis = MIN_MAESTRO + (MAX_MAESTRO - MIN_MAESTRO) * ratio
    return int(quarter_millis)


def main():
    SERVO1 = 0
    SERVO2 = 1

    m = maestro.Controller()

    angle1 = 180
    angle2 = 0

    while True:
        target1 = degrees_to_quarter_millis(angle1)
        target2 = degrees_to_quarter_millis(angle2)

        m.setTarget(SERVO1, target1)
        m.setTarget(SERVO2, target2)
        time.sleep(2)


if __name__ == "__main__":
    main()
