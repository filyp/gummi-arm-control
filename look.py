"""
captures video
detects glyphs and their position
based on
rdmilligan.wordpress.com/2015/07/19/glyph-recognition-using-opencv-and-python/
"""

import cv2
# print(cv2.getBuildInformation())

from look_helpers import *

# tweak these
EDGE_LOWER_THRESHOLD = 50
EDGE_UPPER_THRESHOLD = 100
substitute_image = cv2.imread('substitute.jpg')

# constants
GLYPH_PATTERN = [[0, 1, 0],
                 [1, 0, 0],
                 [0, 1, 1]]
BUILTIN_CAMERA = 0
LOOPBACK_CAMERA = 1


cv2.namedWindow("camera")
vc = cv2.VideoCapture(BUILTIN_CAMERA)        # set to 0 for built in camera


is_open = vc.isOpened()
while is_open:
    is_open, frame = vc.read()

    imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    imgray = cv2.GaussianBlur(imgray, (3, 3), 0)

    edges = cv2.Canny(imgray, EDGE_LOWER_THRESHOLD, EDGE_UPPER_THRESHOLD)
    im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
    number_of_detected = 0
    for contour in contours:
        # approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.03 * peri, True)
        if len(approx) != 4:
            continue

        topdown_quad = get_topdown_quad(imgray, approx.reshape(4, 2))
        bitmap = cv2.resize(topdown_quad, (5, 5))

        glyph_found = False
        for rotation_num in range(4):
            if check_for_pattern(bitmap, GLYPH_PATTERN):
                glyph_found = True
                break
            bitmap = rotate_image(bitmap, 90)

        # cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3)
        if glyph_found:
            number_of_detected += 1
            cv2.imshow("im", bitmap)
            # approx = np.roll(approx, rotation_num)
            frame = add_substitute_quad(frame, substitute_image, approx.reshape(4, 2))
            last_approx = approx
            # cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3)

    # temporary solution for annoying flickering
    # TODO fix image lingering too long
    if number_of_detected == 0:
        try:
            frame = add_substitute_quad(frame, substitute_image, last_approx.reshape(4, 2))
        except:
            pass

    frame = cv2.flip(frame, 1)
    cv2.imshow("camera", frame)

    key = cv2.waitKey(10)
    if key == 27:   # exit on ESC
        break

cv2.destroyWindow("camera")
