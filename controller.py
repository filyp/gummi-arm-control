import glob
import textwrap

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


while True:
    cmd = input()
    if cmd == 'q':
        exit()
    try:
        angle_str, stiffness_str = cmd.split()
        angle, stiffness = int(angle_str), int(stiffness_str)
        controller.send(angle, stiffness)
    except ValueError:
        help_string = f"""
        Type commands that will be sent to the arm.

        command: "<angle> <stiffness>"
        for example: "120 10"
        To quit press 'q'
        """
        print(textwrap.dedent(help_string))
