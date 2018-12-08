from time import time


class MovementController:
    def __init__(self, max_servo_speed=250, stiffness_slope=1):
        """Specify how stiffness should change during movement.

        Changing stiffness_slope won't change the time that movement takes.
        The servo that has more distance to move, will still move at max speed.
        Only the other servo influences how stiff the arm will be during movement.

        Note that it puts some constraints on what stiffnesses can be achieved
        during movement. In extreme case, if final stiffness is the same
        as starting one, and only angle changes, both servos move at max speed,
        so in this case changing stiffness_slope has no effect.

        If you really want to achieve stiffnesses out of these constraints,
        even at the cost of longer movement, you have to call send method more
        than once. For example a good idea would be to call send method with
        a higher target stiffness (it should also damp shaking better),
        and after that movement is finished call send with lower stiffness
        but the same angle.


        Args:
            max_servo_speed:    speed in degrees/second
            stiffness_slope:    float between 0 and 2,
                                0 is lowest possible stiffness during movement,
                                1 means it will change linearly,
                                2 is highest possible

        Notes:
            If given max_servo_speed is larger than real maximum servo speed,
            movement control will be clipped and won't be smooth.

            Parameters passed to this method must be the same as
            passed to Configurator.turn_on_movement_control.
        """
        self.max_servo_speed = max_servo_speed
        self.stiffness_slope = stiffness_slope
        self.completion = 1

    def set_target(self, servo_angle, stiffness):
        self.completion = 0
        # TODO

    def get_command(self):
        # TODO
        pass
