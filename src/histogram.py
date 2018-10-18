
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
        ratio = (ratio + inverted_phi) % 1
        yield int(ratio * length)


class Histogram(SortedList):
    """
    Compare in percentiles how a given value compares to previous values
    Adapts over time, so old values become less relevant
    Bigger length gives better resolution and also longer adaptation time
    Works in O(log(length))
    """

    def __init__(self, max_length):
        SortedList.__init__(self)
        self.max_length = max_length
        self.gen = sunflower_generator(max_length)

    def put(self, value):
        if len(self) >= self.max_length:
            index_to_remove = next(self.gen)
            self.__delitem__(index_to_remove)
        self.add(value)

    def get_percentile(self, value):
        """
        :param value:
        :return: what percentile (0..1) of previous values were smaller than this value
        """
        leftmost = self.bisect_left(value)
        rightmost = self.bisect_right(value)
        average = (leftmost + rightmost) / 2
        return average / len(self)

    def get_value(self, percentile):
        """
        :param percentile: between 0 and 1
        :return: value that is larger than some percentile of previous values
        for example get_value(0.5) to get median
        """
        index = int(percentile * (len(self) - 1))
        return self[index]
