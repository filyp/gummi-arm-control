"""
captures video
detects glyphs and their position
based on
rdmilligan.wordpress.com/2015/07/19/glyph-recognition-using-opencv-and-python/
"""

import os
# print(cv2.getBuildInformation())
import cv2
import subprocess
import threading
import time

from look_helpers import *

# tweak these
EDGE_LOWER_THRESHOLD = 30
EDGE_UPPER_THRESHOLD = 90
# substitute_image = cv2.imread('substitute.jpg')

GLYPH_PATTERNS = {
    "ALPHA": [[0, 1, 0],
              [1, 0, 0],
              [0, 1, 1]],
    "BETA": [[1, 1, 0],
             [0, 0, 0],
             [0, 1, 0]],
    "GAMMA": [[1, 0, 1],
              [0, 1, 0],
              [1, 0, 0]],
    "DELTA": [[1, 0, 1],
              [0, 0, 0],
              [1, 0, 0]]
}

BUILTIN_CAMERA = 0


class TimingOut(object):
    """
    When value is set
    Save the time, reading will fail
    If you read too late
        ~Pope John Paul II
    """

    def __init__(self, timeout):
        self.timeout = timeout
        self.last_assignment_timestamp = 0
        self.value = None

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        self.__dict__['last_assignment_timestamp'] = time.time()

    def __getattr__(self, attr):
        if attr != 'value':
            raise KeyError('No such key found, use value instead')
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
        self.alpha = TimingOut(timeout)
        self.beta = TimingOut(timeout)
        self.gamma = TimingOut(timeout)
        self.delta = TimingOut(timeout)
        self._alive = True

    @staticmethod
    def connect_camera():

        cv2.namedWindow("camera")
        return cv2.VideoCapture(BUILTIN_CAMERA)

    @staticmethod
    def find_contours(imgray):
        edges = cv2.Canny(imgray, EDGE_LOWER_THRESHOLD, EDGE_UPPER_THRESHOLD)
        im2, contours, hierarchy = cv2.findContours(edges,
                                                    cv2.RETR_TREE,
                                                    cv2.CHAIN_APPROX_SIMPLE)
        return sorted(contours, key=cv2.contourArea, reverse=True)[:100]

    def get_angle(self):
        try:
            return calculate_angle_4_glyphs(self.alpha.value,
                                            self.beta.value,
                                            self.gamma.value,
                                            self.delta.value)
        except TimeoutError:
            return None

    def record_glyph_coordinates(self, contours, imgray):
        for contour in contours:
            # approximate the contour
            peri = cv2.arcLength(curve=contour, closed=True)
            approx = cv2.approxPolyDP(curve=contour, epsilon=0.01 * peri, closed=True)
            if len(approx) != 4:
                continue
            topdown_quad = get_topdown_quad(imgray, approx.reshape(4, 2))
            bitmap = cv2.resize(topdown_quad, (5, 5))
            self.recognize_glyph(bitmap, approx)

    def recognize_glyph(self, bitmap, approx):
        for glyph_pattern in GLYPH_PATTERNS:
            for rotation_num in range(4):
                if bitmap_matches_glyph(bitmap, GLYPH_PATTERNS[glyph_pattern]):
                    # cv2.imshow("im", bitmap)
                    flattened = flatten(approx)
                    ordered = order_points(flattened)
                    if glyph_pattern == "ALPHA":
                        self.alpha.value = ordered
                    elif glyph_pattern == "BETA":
                        self.beta.value = ordered
                    elif glyph_pattern == "GAMMA":
                        self.gamma.value = ordered
                    elif glyph_pattern == "DELTA":
                        self.delta.value = ordered
                    break
                bitmap = rotate_image(bitmap, 90)
                angle = self.get_angle()
                # print(self.alpha.value)
                print(angle)

    def run(self):
        while self._alive:
            is_open, frame = self.camera.read()
            if not is_open:
                break
            imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            imgray = cv2.GaussianBlur(imgray, (3, 3), 0)
            contours = self.find_contours(imgray)
            self.record_glyph_coordinates(contours, imgray)

    def kill(self):
        """tell thread to stop gracefully"""
        self._alive = False


ania = PositionDetector(0.1)
ania.start()
