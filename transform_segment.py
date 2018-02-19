# Copyright (C) 2018 Daniel Roudnitsky <droudnitsky@gmail.com>

"""
Since the same character can be different sizes/scales in different equations we need some way of having a fixed length
representation of a character that doesn't change significantly with differences in the characters scale/resolution.
The purpose of `TransformSegment` is to be able to create a fixed size vector representation of segments of different
sizes.
"""

import numpy as np
from PIL import Image


class TransformSegment(object):
    """
    Class that contains methods to transform/manipulate/vectorize a Segment object

    TransformSegment will always transform the passed in segment as close to the origin as possible but the Segment
    object still retains all the information about the segment before it was transformed to the origin
    """

    def __init__(self, segment):
        self.seg = segment
        self.rescale_size = None
        self.transform_to_origin()

    def transform_to_origin(self):
        """
        Transform the segment as close to the origin as possible for proper rescaling
        """
        x_min, y_min = self.seg.upper_left
        self.seg.pix = [(xy[0] - x_min, xy[1] - y_min) for xy in self.seg.pix]

    def rescale(self, size):
        """
        Due to not wanting to implement an image rescaling algorithm: rebuild the image object, rescale using
        PIL and re extract non white pixels. TODO implement rescaling algorithm for increase in speed
        """
        self.rescale_size = size

        # rebuild and resize image
        im = Image.new('RGBA', (self.seg.dimensions[0] + 1, self.seg.dimensions[1] + 1))
        for xy in self.seg.pix:
            im.putpixel(xy, (0, 255, 255, 255))
        im = im.resize(size, Image.ANTIALIAS)

        # extract non white pixels again
        self.seg.pix = []
        pixels = list(im.getdata())
        A_LOWERBOUND = 50  # lower bound for A values from RGBA to keep that are changed due to rescaling
        non_white = lambda x: x[3] > A_LOWERBOUND
        for y in xrange(size[1]):
            for x in xrange(size[0]):
                if non_white(pixels[y * size[1] + x]):
                    self.seg.pix.append((x, y))

    def get_flattened_pix_grid(self, fill_val=-1):
        """
        Create a matrix of size max_X by max_Y where each matrix entry corresponding to a pixel in the segment.
        Non white pixels are represented as 1 and white pixels as `fill_val`. The matrix is then flattened. Meant to be
        used after rescaling the image to compare images using a similarity metric
        :return: One dimensional list of size max_X * max_y TODO
        """
        if self.rescale_size:
            grid = np.empty(self.rescale_size)
        else:
            grid = np.empty(self.seg.dimensions)

        grid.fill(fill_val)
        for xy in self.seg.pix:
            grid[xy[1]][xy[0]] = 1

        return np.ndarray.flatten(grid)


