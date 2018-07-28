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


def overlay(background, overlay_image, approx, rotation_num):
    overlay_image = rotate_image(overlay_image, -rotation_num * 90)

    overlay_height, overlay_width = overlay_image.shape[:2]
    background_height, background_width = background.shape[:2]

    points = np.asarray(
        [np.asarray(x[0], dtype=np.float32) for x in approx],
        dtype=np.float32
    )
    points = order_points(points)

    input_coordinates = np.asarray(
        [
            np.asarray([0, 0], dtype=np.float32),
            np.asarray([overlay_width, 0], dtype=np.float32),
            np.asarray([overlay_width, overlay_height], dtype=np.float32),
            np.asarray([0, overlay_height], dtype=np.float32)
        ],
        dtype=np.float32,
    )

    transformation_matrix = cv2.getPerspectiveTransform(
        np.asarray(input_coordinates),
        np.asarray(points),
    )

    warped_image = cv2.warpPerspective(
        overlay_image,
        transformation_matrix,
        (background_width, background_height),
    )

    alpha_channel = np.ones(overlay_image.shape, dtype=np.float)
    alpha_channel = cv2.warpPerspective(
        alpha_channel,
        transformation_matrix,
        (background_width, background_height),
    )

    def normalize(im):
        min_val = np.min(im.ravel())
        max_val = np.max(im.ravel())
        out = (im.astype('float') - min_val) / (max_val - min_val)
        return out
    background = normalize(background)
    warped_image = normalize(warped_image)
    return (warped_image * alpha_channel) + (background * (1 - alpha_channel))


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
