#!/bin/sh
"exec" "`dirname $0`/env/bin/python" "$0" "$@"
# shebang for virtualenv execution from any location
# credit: stackoverflow.com/questions/20095351

import glob
import textwrap
import time

from Xlib import display
from pyfiglet import figlet_format
from scipy.interpolate import interp1d

from approximation.approximation import DATA_LOCATION
from approximation.position_controller import PositionController
from experiments import collect_data


banner_string = 'GummiControl'
print(figlet_format(banner_string, font='rectangles'))


controller = PositionController()


def mouse_control():
    try:
        root = display.Display().screen().root
        screen_width = root.get_geometry().width
        screen_height = root.get_geometry().height
        stiffness_mapper = interp1d([0, screen_height], [50, -30])
        angle_mapper = interp1d([0, screen_width], [0, 180])
        while True:
            qp = root.query_pointer()
            angle = angle_mapper(qp.root_x)
            stiffness = stiffness_mapper(qp.root_y)
            try:
                controller.send(angle, stiffness)
                print(f'angle: {angle:3.0f}   stiffness: {stiffness:3.0f}')
            except ValueError as err:
                print(err)
            time.sleep(0.001)
    except KeyboardInterrupt:
        print('\nQuited mouse mode')


while True:
    cmd = input()

    if cmd == 'q':
        exit()
    if cmd == 'm':
        mouse_control()
        continue
    try:
        angle_str, stiffness_str = cmd.split()
        angle, stiffness = float(angle_str), float(stiffness_str)
    except ValueError:
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
        print(textwrap.dedent(help_string))
        continue
    try:
        controller.send(angle, stiffness)
    except ValueError as err:
        print(err)


# TODO better mouse range
