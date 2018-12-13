from src.control.PID_regulator.pid import PID

# todo change to 1 - 0.5 % of first error rate
THRESHOLD = 0.2

# better higher P and lower I, but matlab claims different things - only I-component


class PIDController:
    def __init__(self, position_detector, raw_controller, stiffness_function, P=0.7, I=0.2, D=0.2):
        self.pid = PID(P=P, I=I, D=D)
        self.position_detector = position_detector
        self.raw_controller = raw_controller
        # todo evaluate function from string
        self.stiffness_function = stiffness_function

    # def get_current_stiffness_index(self, current_angle, tick):
    #     index = int(current_angle / tick)
    #     return index

    def control(self, target_angle, starting_servo_angle, target_stiffness, starting_position):
        self.pid.set_point(target_angle)
        current_servo_angle = starting_servo_angle
        while True:
            current_angle = self.position_detector.get_angle()

            # calculate stiffness
            movement_completion = (1 - abs(current_angle - target_angle)) / abs(target_angle - starting_position)
            stiffness = self.stiffness_function(movement_completion) * target_stiffness

            if abs(current_angle - target_angle) <= THRESHOLD:
                return
            # stiffness_index = self.get_current_stiffness_index(current_angle, tick)
            # stiffness = stiffness_grid[stiffness_index]

            delta_angle = self.pid.update(current_angle)
            current_servo_angle += delta_angle

            self.raw_controller.send(current_servo_angle, stiffness)

