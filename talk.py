"""
serial communication with arduino
"""

import threading

import serial

from config.constants import PORT, BAUDRATE, PLOT_X_SIZE


class Reader(threading.Thread):
    """
    Reads current measurements from arduino
    and sends them to signal plotter
    TODO not true anymore
    """

    def __init__(self, plot):
        threading.Thread.__init__(self)
        self.plot = plot
        self.ser = serial.Serial(PORT, BAUDRATE)
        self.alive = True

    def run(self):
        while self.alive:
            # parse
            line = self.ser.readline()
            i1, i2 = [float(val) for val in line.split()]

            # send to plotter
            self.plot.add(i1, i2)

        # clean up
        self.ser.flush()
        self.ser.close()

    def kill(self):
        """tell Reader thread to stop safely"""
        self.alive = False


class ServoController:
    """
    Handles mouse events
    and sends corresponding servo commands
    TODO not true anymore
    """

    def __init__(self, plot=None):
        self.ser = serial.Serial(PORT, BAUDRATE)
        self.angle = 0
        self.stiffness = 0
        self.plot = plot

    def set_stiffness(self, event):
        """handle changing stiffness mouse command"""
        self.stiffness += event.step
        self.send()

    def set_angle(self, event):
        """handle changing angle mouse command"""
        if event.inaxes:
            mouse_position = event.xdata / PLOT_X_SIZE
            self.angle = int(mouse_position * 180)
            self.send()

    def send(self):
        """send position to the arm"""
        error_msg = ''

        if self._position_valid():
            self.ser.write(b'A' + self.get_raw_angle1().to_bytes(1, 'little'))
            self.ser.write(b'B' + self.get_raw_angle2().to_bytes(1, 'little'))
        else:
            error_msg = 'servo out of range'

        if self.plot:
            self.plot.info_text = 'angle: {}  stiffness: {}  {}' \
                .format(self.angle, self.stiffness, error_msg)

    def get_raw_angle1(self):
        return self.angle + self.stiffness

    def get_raw_angle2(self):
        return 180 - self.angle + self.stiffness

    def _position_valid(self):
        return 0 <= self.get_raw_angle1() <= 180 and \
               0 <= self.get_raw_angle2() <= 180
