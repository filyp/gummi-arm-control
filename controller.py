#!env/bin/python
import glob
import textwrap
import time

from Xlib import display
from scipy.interpolate import interp1d

from experiments import collect_data
from interpolation.interpolation import DATA_LOCATION
from interpolation.interpolation_position_controller import InterpolationPositionController

banner_string = 'GummiControl'
try:
    import pyfiglet
    banner_string = pyfiglet.figlet_format(banner_string, font='rectangles')
except ImportError:
    pass
print(banner_string)


if not glob.glob(DATA_LOCATION):
    # TODO this section needs testing
    info = """
    Looks like you haven't trained your arm yet.
    
    Connect your arm and camera.
    If you want to use remote camera type in it's address
        example:    '192.168.0.52:4747'
        
    If you want to use built-in or USB camera just hit enter.
    """
    cameara_address = input(textwrap.dedent(info))
    collect_data.start(camera_address=cameara_address)


controller = InterpolationPositionController()


def mouse_control():
    root = display.Display().screen().root
    screen_width = root.get_geometry().width
    screen_height = root.get_geometry().height
    stiffness_mapper = interp1d([0, screen_height], [50, -30])
    angle_mapper = interp1d([0, screen_width], [0, 180])
    while True:
        qp = root.query_pointer()
        angle = angle_mapper(qp.root_x)
        stiffness = stiffness_mapper(qp.root_y)
        print(f'angle: {angle:3.0f}   stiffness: {stiffness:3.0f}')
        controller.send(angle, stiffness, polite=True)
        time.sleep(0.001)


while True:
    cmd = input()
    if cmd == 'q':
        exit()
    if cmd == 'm':
        mouse_control()
    try:
        angle_str, stiffness_str = cmd.split()
        angle, stiffness = int(angle_str), int(stiffness_str)
        controller.send(angle, stiffness, polite=True)
    except ValueError:
        help_string = f"""
        Type commands that will be sent to the arm.

        command: "<angle> <stiffness>"
            for example: "120 10"
            
        To quit press 'q'
        To turn on mouse control press 'm'
        """
        print(textwrap.dedent(help_string))
