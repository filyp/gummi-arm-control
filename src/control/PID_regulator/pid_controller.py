from src.control.PID_regulator.pid import PID

THRESHOLD = 1


class PIDController:
    def __init__(self, position_detector, raw_controller, P=2.0, I=0.0, D=1.0):
        self.pid = PID(P=P, I=I, D=D)
        self.position_detector = position_detector
        self.raw_controller = raw_controller

    def get_current_stiffness_index(self, current_angle, tick):
        index = int(current_angle / tick)
        return index

    def control(self, target_angle, starting_servo_angle, stiffness_grid, tick):
        self.pid.set_point(target_angle)
        current_servo_angle = starting_servo_angle
        while True:
            current_angle = self.position_detector.get_angle()
            if abs(current_angle - target_angle) <= THRESHOLD:
                return
            stiffness_index = self.get_current_stiffness_index(current_angle, tick)
            stiffness = stiffness_grid[stiffness_index]

            delta_angle = self.pid.update(current_angle)
            current_servo_angle += delta_angle
            self.raw_controller.send(current_servo_angle, stiffness)

