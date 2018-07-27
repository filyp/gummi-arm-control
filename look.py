"""
captures video
detects glyphs and their position
based on
rdmilligan.wordpress.com/2015/07/19/glyph-recognition-using-opencv-and-python/
"""

import cv2
# print(cv2.getBuildInformation())

from look_helpers import *


BLACK_THRESHOLD = 130
WHITE_THRESHOLD = 135
SHAPE_RESIZE = 100.0
GLYPH_PATTERN = [0, 1, 0, 1, 0, 0, 0, 1, 1]


cv2.namedWindow("camera")
vc = cv2.VideoCapture(1)        # set to 0 for built in camera


is_open = vc.isOpened()
while is_open:
    is_open, frame = vc.read()

    imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # imgray = cv2.GaussianBlur(imgray, (7, 7), 0)

    edges = cv2.Canny(imgray, 20, 100)
    im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
    for contour in contours:
        # approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) != 4:
            continue
        topdown_quad = get_topdown_quad(imgray, approx.reshape(4, 2))
        resized_shape = resize_image(topdown_quad, SHAPE_RESIZE)

        # if resized_shape[5, 5] > BLACK_THRESHOLD:
        #     # ???
        #     continue

        glyph_found = False

        for i in range(4):
            try:
                glyph_pattern = get_glyph_pattern(resized_shape, BLACK_THRESHOLD, WHITE_THRESHOLD)
            except:
                pass

            if glyph_pattern == GLYPH_PATTERN:
                glyph_found = True
                break

            resized_shape = rotate_image(resized_shape, 90)
        if glyph_found:
            # cv2.drawContours(frame, [approx], -1, (0, 255, 0), 4)
            substitute_image = cv2.imread('substitute.jpg')
            frame = add_substitute_quad(frame, substitute_image, approx.reshape(4, 2))

    # cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)
    cv2.imshow("camera", frame)

    key = cv2.waitKey(10)
    if key == 27:   # exit on ESC
        break

cv2.destroyWindow("camera")
