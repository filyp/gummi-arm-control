
import threading

import serial

from config import PORT, BAUDRATE, PLOT_X_SIZE


class Reader(threading.Thread):
    """
    Reads current measurements from arduino
    and sends them to signal plotter
    """

    def __init__(self, plot):
        threading.Thread.__init__(self)
        self.plot = plot
        self.ser = serial.Serial(PORT, BAUDRATE)
        self.alive = True
        self.avg = 0
        self.counter = 0

    def run(self):
        # last_time = time()
        while self.alive:
            # # measure latency
            # t = time()
            # print((t - last_time)*1000)
            # last_time = t

            # parse
            line = self.ser.readline()
            data = [float(val) for val in line.split()]

            # send to plotter
            self.plot.add(data)

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
    """

    def __init__(self, plot):
        self.ser = serial.Serial(PORT, BAUDRATE)
        self.angle = 0
        self.stiffness = 0
        self.plot = plot

    def set_stiffness(self, event):
        """handle changing stiffness mouse commend"""
        self.stiffness += event.step
        self.send()

    def set_angle(self, event):
        """handle changing angle mouse commend"""
        if event.inaxes:
            mouse_position = event.xdata / PLOT_X_SIZE
            self.angle = int(mouse_position * 180)
            self.send()

    def send(self):
        """send position to the arm"""
        angle1 = self.angle + self.stiffness
        angle2 = 180 - self.angle + self.stiffness
        error_msg = ''

        if 0 <= angle1 <= 180 and 0 <= angle2 <= 180:
            self.ser.write(b'A' + angle1.to_bytes(1, 'little'))
            self.ser.write(b'B' + angle2.to_bytes(1, 'little'))
        else:
            error_msg = 'servo out of range'

        self.plot.info_text = 'angle: {}  stiffness: {}  {}' \
            .format(self.angle, self.stiffness, error_msg)
