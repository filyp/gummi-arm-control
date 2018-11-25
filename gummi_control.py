#!/bin/sh
"exec" "`dirname $0`/env/bin/python" "$0" "$@"
# shebang for virtualenv execution from any location
# credit: stackoverflow.com/questions/20095351

import glob
import textwrap
from time import time, sleep

from Xlib.display import Display
from pyfiglet import figlet_format
from scipy.interpolate import interp1d

from approximation.approximation import DATA_LOCATION
from approximation.position_controller import PositionController
from experiments import collect_data


banner_string = 'GummiControl'
print(figlet_format(banner_string, font='rectangles'))


class MouseHandler:
    def __init__(self, min_angle=50, max_angle=180):
        self.root = Display().screen().root
        screen_width = self.root.get_geometry().width
        screen_height = self.root.get_geometry().height

        self.stiffness_mapper = interp1d([0, screen_height],
                                         [50, -30])
        self.angle_mapper = interp1d([0, screen_width],
                                     [min_angle, max_angle])

    def get_cmd_from_mouse_position(self):
        qp = self.root.query_pointer()
        angle = self.angle_mapper(qp.root_x)
        stiffness = self.stiffness_mapper(qp.root_y)
        return angle, stiffness

    def continuous_control(self, controller, timeout=float('inf')):
        last_cmd = None
        last_update_time = time()
        while time() - last_update_time < timeout:
            sleep(0.001)
            cmd = self.get_cmd_from_mouse_position()
            if cmd == last_cmd:
                continue
            last_cmd = cmd
            last_update_time = time()
            angle, stiffness = cmd
            try:
                controller.send(angle, stiffness)
                print(f'angle: {angle:3.0f}   stiffness: {stiffness:3.0f}')
            except ValueError as err:
                print(err)


if __name__ == '__main__':
    help_string = f"""
    Type commands that will be sent to the arm:
        command:     "<angle> <stiffness>"
        for example: "120 10"

    Mouse control:
        press 'm' to turn on
        CTRL+C to turn off
        move mouse left-right to control arm position
        move mouse up-down to control arm stiffness

    Quit:
        press 'q'
    """
    controller = PositionController()
    mouse_handler = MouseHandler()
    while True:
        cmd = input()

        if cmd == 'q':
            exit()
        if cmd == 'm':
            try:
                mouse_handler.continuous_control(controller, timeout=10)
            except KeyboardInterrupt:
                pass
            print('\nQuited mouse mode')
            continue

        try:
            angle_str, stiffness_str = cmd.split()
            angle, stiffness = float(angle_str), float(stiffness_str)
        except ValueError:
            print(textwrap.dedent(help_string))
            continue
        try:
            controller.send(angle, stiffness)
        except ValueError as err:
            print(err)
