from PID.pid import PID


class PIDController:
    def __init__(self, position_detector, raw_controller, P=2.0, I=0.0, D=1.0):
        self.pid = PID(P=P, I=I, D=D)
        self.position_detector = position_detector
        self.raw_controller = raw_controller

    def control(self, target_angle, starting_servo_angle, stiffness):
        self.pid.set_point(target_angle)
        current_servo_angle = starting_servo_angle
        while True:
            current_angle = self.position_detector.get_angle()
            delta_angle = self.pid.update(current_angle)
            current_servo_angle += delta_angle
            self.raw_controller.send(current_servo_angle, stiffness)
