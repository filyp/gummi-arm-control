"""
captures video
detects glyphs and their position
based on
rdmilligan.wordpress.com/2015/07/19/glyph-recognition-using-opencv-and-python/
"""

import cv2
import os
# print(cv2.getBuildInformation())

from look_helpers import *

# tweak these
EDGE_LOWER_THRESHOLD = 30
EDGE_UPPER_THRESHOLD = 90
substitute_image = cv2.imread('substitute.jpg')

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

BUILTIN_CAMERA = 0
LOOPBACK_CAMERA = 1

# current glyphs coordinates
TOP_GLYPH_COORDINATES = None
LOWER_GLYPH_COORDINATES = None
LOWER_GLYPH_ROTATION_NUM = None

# # bind camera to /dev/video1
# os.spawnl(os.P_NOWAIT,
#           'gphoto2 --stdout --capture-movie | \
#                 gst-launch-1.0 fdsrc fd=0 ! decodebin name=dec ! queue ! \
#                 videoconvert ! tee ! v4l2sink device=/dev/video1')

cv2.namedWindow("camera")
vc = cv2.VideoCapture(BUILTIN_CAMERA)

is_open = vc.isOpened()

while is_open:
    is_open, frame = vc.read()
    canvas = np.zeros(frame.shape, np.uint8)
    imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    imgray = cv2.GaussianBlur(imgray, (3, 3), 0)

    edges = cv2.Canny(imgray, EDGE_LOWER_THRESHOLD, EDGE_UPPER_THRESHOLD)
    im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:100]

    number_of_detected = 0
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
                    cv2.imshow("im", bitmap)

                    flattened = flatten(approx)
                    ordered = order_points(flattened)

                    if glyph_pattern == "UPPER":
                        TOP_GLYPH_COORDINATES = ordered
                    elif glyph_pattern == "LOWER":
                        LOWER_GLYPH_COORDINATES = ordered
                    elif glyph_pattern == "ANGLE":
                        LOWER_GLYPH_ROTATION_NUM = rotation_num
                    break
                bitmap = rotate_image(bitmap, 90)

        angle = calculate_angle(TOP_GLYPH_COORDINATES, LOWER_GLYPH_COORDINATES, LOWER_GLYPH_ROTATION_NUM)
        print(angle)
    # temporary solution for annoying flickering
    # # TODO fix image lingering too long
    # if number_of_detected == 0:
    #     try:
    #         frame = overlay(frame, substitute_image, last_approx, 0)
    #     except:
    #         pass

    frame = cv2.flip(frame, 1)
    cv2.imshow("camera", frame)

    key = cv2.waitKey(10)
    if key == 27:  # exit on ESC
        break

cv2.destroyWindow("camera")
