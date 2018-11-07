"""
serial communication with arduino
"""

import threading
import time

import numpy as np
import serial

from config.constants import PORT, BAUDRATE, MAX_ANGLE


class Reader(threading.Thread):
    """
    Reads current measurements from arduino,
    calibrate to find min and max values,
    once calibrated rescales raw values
    and sends them to signal plotter
    """

    CALLIBRATION_TIME = 3

    def __init__(self, plot):
        threading.Thread.__init__(self)
        self.plot = plot
        self.ser = serial.Serial(PORT, BAUDRATE)
        self._die = threading.Event()

        self.i1_min = 1024
        self.i1_max = 0
        self.i2_min = 1024
        self.i2_max = 0

    def read_raw_values(self):
        line = self.ser.readline()
        return [float(val) for val in line.split()]

    def run(self):
        print('calibrating...')
        print('please, put some load on servos')
        start_time = time.time()
        while time.time() - start_time < self.CALLIBRATION_TIME:
            i1, i2 = self.read_raw_values()
            self.i1_min = min(self.i1_min, i1)
            self.i1_max = max(self.i1_max, i1)
            self.i2_min = min(self.i2_min, i2)
            self.i2_max = max(self.i2_max, i2)
        print('calibrating finished')

        while not self._die.is_set():
            i1, i2 = self.read_raw_values()

            # map raw data into 0..1 interval
            i1 = np.interp(i1, [self.i1_min, self.i1_max], [0, 1])
            i2 = np.interp(i2, [self.i2_min, self.i2_max], [0, 1])

            # send to plotter
            self.plot.add(i1, i2)

        # clean up
        self.ser.flush()
        self.ser.close()

    def kill(self):
        """tell thread to stop gracefully"""
        self._die.set()


class ServoController(threading.Thread):
    """
    Connect by serial
    Set position and stiffness
    Send them to servos
    """
    def __init__(self, plot=None):
        threading.Thread.__init__(self)
        self.ser = serial.Serial(PORT, BAUDRATE)
        self.angle = 0
        self.stiffness = 0
        self.plot = plot
        self._die = threading.Event()

    def get_raw_angle1(self):
        return self.angle + self.stiffness

    def get_raw_angle2(self):
        return self.angle - self.stiffness

    def _position_valid(self):
        """return if the saved position is inside the servos range"""
        return 0 <= self.get_raw_angle1() <= MAX_ANGLE and \
               0 <= self.get_raw_angle2() <= MAX_ANGLE

    def send(self):
        """send saved position to the arm"""
        error_msg = ''

        if self._position_valid():
            self.ser.write(b'A' + self.get_raw_angle1().to_bytes(1, 'little'))
            self.ser.write(b'B' + self.get_raw_angle2().to_bytes(1, 'little'))
        else:
            error_msg = 'servo out of range'

        if self.plot:
            self.plot.info_text = 'angle: {}  stiffness: {}  {}' \
                .format(self.angle, self.stiffness, error_msg)

    def run(self):
        while not self._die.is_set():
            self.send()
            time.sleep(0.01)

    def kill(self):
        self._die.set()
