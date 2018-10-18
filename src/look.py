"""
captures video
detects glyphs and their position
based on
rdmilligan.wordpress.com/2015/07/19/glyph-recognition-using-opencv-and-python/
"""

import os
# print(cv2.getBuildInformation())
import subprocess
import threading
import time

from src.look_helpers import *

# tweak these
EDGE_LOWER_THRESHOLD = 30
EDGE_UPPER_THRESHOLD = 90
# substitute_image = cv2.imread('substitute.jpg')

GLYPH_PATTERNS = {
    "UPPER": [[0, 1, 0],
              [1, 0, 0],
              [0, 1, 1]],
    "LOWER": [[1, 1, 0],
              [0, 0, 0],
              [0, 1, 0]],
    "ANGLE": [[1, 0, 1],
              [0, 0, 0],
              [1, 0, 0]]
}


class TimingOut:
    """
    When value is set
    Save the time, reading will fail
    If you read too late
    """
    def __init__(self, timeout):
        self.timeout = timeout
        self.last_assignment_timestamp = 0
        self.v = None

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        self.__dict__['last_assignment_timestamp'] = time.time()

    def __getattr__(self, attr):
        if attr != 'v':
            raise KeyError('No such key found, use v instead')
        if time.time() > self.last_assignment_timestamp + self.timeout:
            raise TimeoutError('Variable timed out')
        return self.__dict__[attr]


class PositionDetector(threading.Thread):
    """
    Connect camera
    Detect marker positions
    Find out their angle
        ~John Paul Jones
    """
    def __init__(self, timeout):
        threading.Thread.__init__(self)
        # self.camera = self.connect_camera(external=True)
        self.camera = cv2.VideoCapture(0)
        # current glyphs coordinates
        self.top_glyph_coordinates = TimingOut(timeout)
        self.lower_glyph_coordinates = TimingOut(timeout)
        self.lower_glyph_rotation_num = TimingOut(timeout)
        self._alive = True

    @staticmethod
    def connect_camera(external=False):
        if not external:
            if not os.path.exists('/dev/video0'):
                raise IOError('No builtin camera found')
            return cv2.VideoCapture(0)
        # create loopback if it doesn't exist already
        if not os.path.exists('/dev/video1'):
            subprocess.run('sudo modprobe v4l2loopback', shell=True)
        if not os.path.exists('/dev/video1'):
            # there was no builtin camera so the created loopback is /dev/video0
            camera_num = 0
        else:
            # created loopback is /dev/video1
            camera_num = 1
        cmd = 'gphoto2 --stdout --capture-movie | ' \
              'gst-launch-1.0 fdsrc fd=0 ! decodebin name=dec ! queue ! ' \
              'videoconvert ! tee ! v4l2sink device=/dev/video{}'.format(camera_num)
        subprocess.Popen(cmd, shell=True)  # run in background
        return cv2.VideoCapture(camera_num)

    @staticmethod
    def find_contours(imgray):
        edges = cv2.Canny(imgray, EDGE_LOWER_THRESHOLD, EDGE_UPPER_THRESHOLD)
        im2, contours, hierarchy = cv2.findContours(edges,
                                                    cv2.RETR_TREE,
                                                    cv2.CHAIN_APPROX_SIMPLE)
        return sorted(contours, key=cv2.contourArea, reverse=True)[:100]

    def get_angle(self):
        try:
            return calculate_angle(self.top_glyph_coordinates.v,
                                   self.lower_glyph_coordinates.v,
                                   self.lower_glyph_rotation_num.v)
        except TimeoutError:
            return None

    def run(self):
        while self._alive:
            is_open, frame = self.camera.read()
            if not is_open:
                break
            imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            imgray = cv2.GaussianBlur(imgray, (3, 3), 0)
            contours = self.find_contours(imgray)

            for contour in contours:
                # approximate the contour
                peri = cv2.arcLength(curve=contour, closed=True)
                approx = cv2.approxPolyDP(curve=contour, epsilon=0.01 * peri, closed=True)
                if len(approx) != 4:
                    continue
                topdown_quad = get_topdown_quad(imgray, approx.reshape(4, 2))
                bitmap = cv2.resize(topdown_quad, (5, 5))

                for glyph_pattern in GLYPH_PATTERNS:
                    for rotation_num in range(4):
                        if bitmap_matches_glyph(bitmap, GLYPH_PATTERNS[glyph_pattern]):
                            # cv2.imshow("im", bitmap)
                            flattened = flatten(approx)
                            ordered = order_points(flattened)
                            if glyph_pattern == "UPPER":
                                self.top_glyph_coordinates.v = ordered
                            elif glyph_pattern == "LOWER":
                                self.lower_glyph_coordinates.v = ordered
                            elif glyph_pattern == "ANGLE":
                                self.lower_glyph_rotation_num.v = rotation_num
                            break
                        bitmap = rotate_image(bitmap, 90)

    def kill(self):
        """tell thread to stop gracefully"""
        self._alive = False
