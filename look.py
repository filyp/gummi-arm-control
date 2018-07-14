"""
captures video
detects glyphs and their position
based on
rdmilligan.wordpress.com/2015/07/19/glyph-recognition-using-opencv-and-python/
"""

import cv2

cv2.namedWindow("camera")
vc = cv2.VideoCapture(0)

rval = vc.isOpened()
while rval:
    rval, frame = vc.read()

    imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    imgray = cv2.GaussianBlur(imgray, (7, 7), 0)

    edges = cv2.Canny(imgray, 20, 100)
    im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

    cv2.imshow("camera", frame)

    key = cv2.waitKey(20)
    if key == 27:   # exit on ESC
        break

cv2.destroyWindow("camera")
