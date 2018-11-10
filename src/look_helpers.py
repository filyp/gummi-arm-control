# credit: rdmilligan.wordpress.com/2015/07/19/glyph-recognition-using-opencv-and-python/

import numpy as np
import cv2
from scipy.spatial import distance as dist


class Point2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "x: {}, y:{}".format(self.x, self.y)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Vector: x: {}, y: {}".format(self.x, self.y)

    def unit_vector(self):
        vector_length = np.sqrt(self.x ** 2 + self.y ** 2)
        return Vector(self.x / vector_length, self.y / vector_length)


def to_point2d(point):
    return Point2d(point[0], point[1])


def to_vector(point_a, point_b):
    return Vector(point_b.x - point_a.x, point_b.y - point_a.y)


def max_width_height(points):
    (tl, tr, br, bl) = points

    top_width = np.sqrt(((tr.x - tl.x) ** 2) + ((tr.y - tl.y) ** 2))
    bottom_width = np.sqrt(((br.x - bl.x) ** 2) + ((br.y - bl.y) ** 2))
    max_width = max(int(top_width), int(bottom_width))

    left_height = np.sqrt(((tl.x - bl.x) ** 2) + ((tl.y - bl.y) ** 2))
    right_height = np.sqrt(((tr.x - br.x) ** 2) + ((tr.y - br.y) ** 2))
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

    np_array = np.array([[point.x, point.y] for point in src])

    # warp perspective
    matrix = cv2.getPerspectiveTransform(np_array, dst)
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
    clockwise_array = np.array([tl, tr, br, bl], dtype="float32")
    return [to_point2d(point) for point in clockwise_array]


#   ordered top-down
def calculate_angle_4_glyphs(alpha, beta, gamma, delta):
    if alpha is None or beta is None or gamma is None or delta is None:
        return None
    else:
        alpha_center = get_center_of_rectangle(alpha[0], alpha[2])
        beta_center = get_center_of_rectangle(beta[0], beta[2])
        gamma_center = get_center_of_rectangle(gamma[0], gamma[2])
        delta_center = get_center_of_rectangle(delta[0], delta[2])

        upper_vector = to_vector(beta_center, alpha_center)
        lower_vector = to_vector(gamma_center, delta_center)

        upper_vector_u = upper_vector.unit_vector()
        lower_vector_u = lower_vector.unit_vector()

        dot = np.dot([upper_vector_u.x, upper_vector_u.y], [lower_vector_u.x, lower_vector_u.y])
        clip = np.clip(dot, -1.0, 1.0)
        # print(np.arccos(clip))
        return ((np.arccos(clip))*180) / 3.1415


def get_center_of_rectangle(point_a, point_b):
    # print(point_b)
    # print(point_a)
    x = (point_a.x + point_b.x) / 2
    y = (point_a.y + point_b.y) / 2

    return Point2d(x, y)


def get_top_coordinates(lower_glyph_coordinates, rotation_num):
    sorted_coordinates = sorted(lower_glyph_coordinates, key=lambda x: x[1])
    if rotation_num == 2:
        return sorted_coordinates[0], sorted_coordinates[1]
    else:
        return sorted_coordinates[1], sorted_coordinates[0]


def flatten(nested_array):
    return np.array(list(points for points_pair in nested_array for points in points_pair))
