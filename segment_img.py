# Copyright (C) 2018 Daniel Roudnitsky <droudnitsky@gmail.com>

"""
An image of a mathematical equation such as 3x + 5 consists of four individual groups of pixels, one group making up the
3, another group of pixels making up the x, another for the plus sign and another one making up the 5. Each of these
groups of pixels is considered a segment. This module identifies the individual segments/groups of pixels that make up
an image (but does not know their classification)
"""

import sys

from PIL import Image
from numpy import ones


class Segment(object):
    """
    Represents a single segment that is segmented from an image. A segment is a group of pixels all located next to each
    other and can represent anything: A digit(0-9), operator(addition, subtraction, etc), letter(a-Z), etc.
    """

    def __init__(self, pixels):
        self.pix = pixels
        self.classification = None  # won't get classified until later, we dont know what the pixels represent right now
        self.describe_pixels()

    def describe_pixels(self):
        """
        Extract information describing the group of pixels and store the info in attributes
        """
        x_min, y_min = self.pix[0][0], self.pix[0][1]  # just to initialize to a known value
        x_max, y_max = 0, 0
        for xy in self.pix:
            if xy[0] < x_min:
                x_min = xy[0]
            if xy[0] > x_max:
                x_max = xy[0]
            if xy[1] < y_min:
                y_min = xy[1]
            if xy[1] > y_max:
                y_max = xy[1]

        self.centroid = ((x_min + x_max) / 2.0), ((y_min + y_max) / 2.0)  # close enough to real centroid
        self.upper_left = (x_min, y_min)  # upper left most coordinate of the rectangle enclosing the segment
        self.lower_right = (x_max, y_max)  # lower right most coordinate of the rectangle enclosing the segment
        self.dimensions = (x_max - x_min, y_max - y_min)

    def show_segment(self):
        """
        Create and show an image of the segment
        """
        im_size = (self.lower_right[0] + 1, self.lower_right[1] + 1)
        im = Image.new('RGBA', im_size)
        for xy in self.pix:
            im.putpixel(xy, (0, 255, 255, 255))
        im.show()

    def __str__(self):
        return "Label: %s \nCentroid: (%f, %f) \nDimensions: (%f, %f)\n" % (self.classification,
                                                                            self.centroid[0],
                                                                            self.centroid[1],
                                                                            self.dimensions[0],
                                                                            self.dimensions[1])


class ImageSegmenter(object):
    """
    Class that segments the characters/symbols/numbers/etc in an image into individual `Segment` objects
    """

    def __init__(self, img):
        if type(img) is str:
            self.img = Image.open(img)
        else:
            self.img = img

        # pixels that are yet to be checked if they are part of a segment
        self.pixels_to_scan = ones((self.img.size[1], self.img.size[0]))
        self.rgba_matrix = self.get_rgba_matrix()

    def segment_image(self, min_pixels=30):
        """
        Search for groups of non-white pixels that are directly connected(next to one another)

        :param min_pixels: Minimum number of pixels that constitute a segment
        :return: List of `Segment` objects
        """
        # segmentation algo is recursive and will call itself as many times as there are pixels in the largest segment
        sys.setrecursionlimit(15000)
        segments = []
        for y in xrange(self.img.size[1]):
            for x in xrange(self.img.size[0]):
                if self.pixels_to_scan[y][x] == 1:
                    pixel_group = self.scan_pixel((x, y), [])
                    if len(pixel_group) > min_pixels:
                        segments.append(Segment(pixel_group))
        return segments

    def scan_pixel(self, xy, segment):
        """
        Recursively search for non-white pixels surrounding `xy` and add them to `segment` until there are only white
        pixels surrounding all the non-white pixels that make up `segment`
        """
        self.pixels_to_scan[xy[1]][xy[0]] = 0
        if xy not in segment and self.is_not_white(xy):
            segment.append(xy)
            surrounding = self.get_surrounding_pixels(xy)
            for pix in surrounding:
                if self.pixels_to_scan[pix[1]][pix[0]] != 0:
                    self.scan_pixel(pix, segment)
        return segment

    def get_surrounding_pixels(self, xy):
        """
        Return list of pixels surrounding xy, usually 4 unless at a border
        """
        x, y = xy[0], xy[1]
        surrounding = [(x, y - 1),
                       (x - 1, y), (x + 1, y),
                       (x, y + 1)]
        out_of_bounds = lambda xy: xy[0] < 0 or xy[1] < 0 or xy[0] >= self.img.size[0] or xy[1] >= self.img.size[1]
        return [xy for xy in surrounding if not out_of_bounds(xy)]

    def get_rgba_matrix(self):
        """
        Return a two dimensional list in the same shape as the image. The zeroeth index contains the list of RGBA
        values of all the pixels in the zeroeth row

        rgba_matrix[5][1] contains a tuple for the rgba values of the pixel in the coordinate (1, 5)
        """
        width, height = self.img.size[0], self.img.size[1]
        pixels = list(self.img.getdata())
        pixel_matrix = []
        for row in xrange(height):
            pixel_matrix.append(pixels[row * width:(row + 1) * width])
        return pixel_matrix

    def is_not_white(self, xy):
        """
        Check if a pixel is non white
        """
        if self.rgba_matrix[xy[1]][xy[0]] != (255, 255, 255, 255):
            return True
        return False


