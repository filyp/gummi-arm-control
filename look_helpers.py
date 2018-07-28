# credit: rdmilligan.wordpress.com/2015/07/19/glyph-recognition-using-opencv-and-python/

import numpy as np
import cv2


def order_points(points):
    s = points.sum(axis=1)
    diff = np.diff(points, axis=1)

    ordered_points = np.zeros((4, 2), dtype="float32")

    ordered_points[0] = points[np.argmin(s)]
    ordered_points[2] = points[np.argmax(s)]
    ordered_points[1] = points[np.argmin(diff)]
    ordered_points[3] = points[np.argmax(diff)]

    return ordered_points


def max_width_height(points):
    (tl, tr, br, bl) = points

    top_width = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    bottom_width = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    max_width = max(int(top_width), int(bottom_width))

    left_height = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    right_height = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    max_height = max(int(left_height), int(right_height))

    return (max_width, max_height)


def topdown_points(max_width, max_height):
    return np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]], dtype="float32")


def get_topdown_quad(image, src):
    # src and dst points
    src = order_points(src)

    (max_width, max_height) = max_width_height(src)
    dst = topdown_points(max_width, max_height)

    # warp perspective
    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(image, matrix, max_width_height(src))

    # return top-down quad
    return warped


def add_substitute_quad(image, substitute_quad, dst):
    # dst (zero-set) and src points
    dst = order_points(dst)

    (tl, tr, br, bl) = dst
    min_x = min(int(tl[0]), int(bl[0]))
    min_y = min(int(tl[1]), int(tr[1]))

    for point in dst:
        point[0] = point[0] - min_x
        point[1] = point[1] - min_y

    (max_width, max_height) = max_width_height(dst)
    src = topdown_points(max_width, max_height)

    # warp perspective (with white border)
    substitute_quad = cv2.resize(substitute_quad, (max_width, max_height))

    warped = np.zeros((max_height, max_width, 3), np.uint8)
    warped[:, :, :] = 255

    matrix = cv2.getPerspectiveTransform(src, dst)
    cv2.warpPerspective(substitute_quad, matrix, (max_width, max_height), warped, borderMode=cv2.BORDER_TRANSPARENT)

    # add substitute quad
    image[min_y:min_y + max_height, min_x:min_x + max_width] = warped

    return image


def check_for_pattern(bitmap, glyph_pattern_centre):
    glyph_pattern = np.pad(glyph_pattern_centre, pad_width=1,
                           mode='constant', constant_values=0)

    # compute bit detection threshold
    number_of_white = np.sum(glyph_pattern)
    sorted_fields = np.sort(bitmap, axis=None)  # sort the flattened bitmap
    darkest_white = sorted_fields[-number_of_white]
    brightest_dark = sorted_fields[-number_of_white - 1]
    threshold = np.average([darkest_white, brightest_dark])

    detector = lambda val: val > threshold
    detected_pattern = detector(bitmap)
    if np.array_equal(detected_pattern, glyph_pattern):
        # print(brightest_dark, darkest_white)
        # print(threshold)
        return True
    return False


def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, rotation_matrix, (w, h))
