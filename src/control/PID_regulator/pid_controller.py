from time import sleep, time

from src.control.PID_regulator.pid import PID
import logging


# better higher P and lower I, but matlab claims different things - only I-component


class PIDController:
    timeout = 10
    """See control method."""
    # TODO time_grain can be specified in configuration
    time_grain = 0.5
    """See control method."""
    # TODO change this class to a thread, so control method can be non-blocking

    def __init__(self, position_detector, raw_controller,
                 stiffness_function_string, P=0.7, I=0.2, D=0.2,
                 interception_moment=None):
        self.pid = PID(P=P, I=I, D=D)
        self.position_detector = position_detector
        self.raw_controller = raw_controller
        self.stiffness_function = eval(stiffness_function_string)
        self.interception_moment = interception_moment
        self.threshold_ratio = 0.05

    # def get_current_stiffness_index(self, current_angle, tick):
    #     index = int(current_angle / tick)
    #     return index

    def wait_for_interception(self, starting_angle, target_angle):
        """Wait until arm is close enough to target angle.

        Reads current arm angle from PositionDetector.
        If the arm travelled more than some ratio of the distance
        between starting_angle and target_angle, method returns.
        That ratio must be specified in self.interception_moment.

        Args:
            starting_angle (float):   angle in which arm started
            target_angle (float):     angle that we want to move the arm to

        """
        distance = abs(target_angle - starting_angle)
        while True:
            current_angle = self.position_detector.get_angle()
            movement_completion = 1 - abs(current_angle - target_angle) / distance
            if movement_completion > self.interception_moment:
                return
            sleep(0.001)

    def control(self, target_angle, starting_servo_angle, target_stiffness, starting_position):
        """Move arm to given angle using PID control.

        Time between sending updates can be specified by time_grain
        class attribute.

        Args:
            target_angle (float): angle that the arm should move to
            starting_servo_angle (float): last angle that was sent
                to RawController
            target_stiffness (float): stiffness that we'd like to achieve
                at the end of the movement
            starting_position (float): arm position, measured by PositionDetector

        Notes:
            This method is blocking. It terminates if we reach position
            that is less than some ratio of the initial error.
            This ratio can be set by threshold_ratio class attribute.
            It also terminates if we don't reach this position
            in time specified by timeout attribute.

        """
        start_time = time()
        self.pid.set_point(target_angle)
        starting_stiffness = 0
        current_servo_angle = starting_servo_angle
        logging.debug(f'Current servo angle: {current_servo_angle}')
        threshold = abs(target_angle - starting_position) * self.threshold_ratio

        current_angle = self.position_detector.get_angle()
        while abs(current_angle - target_angle) > threshold:
            if time() - start_time > self.timeout:
                logging.warning(f"PID control couldn't reach destination "
                                f"in {self.timeout} seconds, so it timed out.")
                return

            logging.debug(f'Current arm angle: {current_angle}')

            # calculate stiffness
            movement_completion = ((current_angle + starting_position) / abs(target_angle - starting_position))
            stiffness = (self.stiffness_function(movement_completion) * (target_stiffness - starting_stiffness)) + \
                        starting_stiffness

            delta_angle = self.pid.update(current_angle)
            logging.debug(f'Delta angle: {delta_angle}')
            current_servo_angle -= delta_angle

            self.raw_controller.send(int(current_servo_angle), stiffness)
            sleep(self.time_grain)
            current_angle = self.position_detector.get_angle()
