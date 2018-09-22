
import numpy as np
from sortedcontainers import SortedList


def sunflower_generator(length):
    """
    Generate integer values between 0 and length-1
    so that they are evenly distributed
    and spread apart maximally
    """
    inverted_phi = 2 / (np.sqrt(5) + 1)
    ratio = 0
    while True:
        ratio += inverted_phi
        ratio %= 1
        yield int(ratio * length)


class Histogram(object):
    """
    Compare in percentiles how a given value compares to previous values
    Adapts over time, so old values become less relevant
    Bigger length gives better resolution and also longer adaptation time
    Works in O(n log(n)) where n is length
    """

    def __init__(self, length):
        self.length = length
        self.histogram = SortedList()
        self.gen = sunflower_generator(length)

    def add(self, value):
        if len(self.histogram) >= self.length:
            to_remove = self.histogram[next(self.gen)]
            self.histogram.remove(to_remove)
        self.histogram.add(value)

    def get_percentile(self, value):
        """
        :param value:
        :return: what percentile (0..1) of previous values were smaller than this value
        """
        leftmost = self.histogram.bisect_left(value)
        rightmost = self.histogram.bisect_right(value)
        average = (leftmost + rightmost) / 2
        return average / len(self.histogram)

    def get_value(self, percentile):
        """
        :param percentile: between 0 and 1
        :return: value that is larger than some percentile of previous values
        for example get_value(0.5) to get median
        """
        index = int(percentile * (len(self.histogram) - 1))
        return self.histogram[index]
