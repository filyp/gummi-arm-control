import csv
import time

import numpy as np

import look
import talk

import numpy as np
import serial

from config.constants import PORT, BAUDRATE, MAX_ANGLE


def main():
    ser = serial.Serial(PORT, BAUDRATE)
    servo1 = 180
    servo2 = 180

    print('dupa send valid')
    while True:
        ser.write(b'A' + servo1.to_bytes(1, 'little'))
        ser.write(b'B' + servo2.to_bytes(1, 'little'))
        time.sleep(2)


if __name__ == "__main__":
    main()
