# credit: rdmilligan.wordpress.com/2015/07/19/glyph-recognition-using-opencv-and-python/

import numpy as np
import cv2
from scipy.spatial import distance as dist


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


def bitmap_matches_glyph(bitmap, glyph_pattern_centre):
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
    # print(image)
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, rotation_matrix, (w, h))


def order_points(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    (br, tr) = rightMost[np.argsort(D)[::-1], :]

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")


def calculate_angle(upper_glyph_coordinates, lower_glyph_coordinates, rotation_num):
    if upper_glyph_coordinates is None or lower_glyph_coordinates is None or rotation_num is None:
        return None
    else:
        lower_top_coordinates = get_top_coordinates(lower_glyph_coordinates, rotation_num)
        upper_side_coordinates = upper_glyph_coordinates[1], upper_glyph_coordinates[2]

        upper_vector = vector(*upper_side_coordinates)
        lower_vector = vector(*lower_top_coordinates)

        upper_vector_u = unit_vector(upper_vector)
        lower_vector_u = unit_vector(lower_vector)

        dot = np.dot(upper_vector_u, lower_vector_u)
        clip = np.clip(dot, -1.0, 1.0)
        return np.arccos(clip)


def get_top_coordinates(lower_glyph_coordinates, rotation_num):
    sorted_coordinates = sorted(lower_glyph_coordinates, key=lambda x: x[1])
    if rotation_num == 2:
        return sorted_coordinates[0], sorted_coordinates[1]
    else:
        return sorted_coordinates[1], sorted_coordinates[0]


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def vector(point_a, point_b):
    return point_b - point_a


def flatten(nested_array):
    return np.array(list(points for points_pair in nested_array for points in points_pair))
