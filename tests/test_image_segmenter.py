# Copyright (C) 2018 Daniel Roudnitsky <droudnitsky@gmail.com>

import unittest

from PIL import Image
from segment_img import ImageSegmenter


class TestImageSegmenter(unittest.TestCase):

    def setUp(self):
        self.img = Image.new('RGBA', (7, 7), (255, 255, 255, 255))
        self.segment = [(2, 1), (3, 1), (4, 1), (5, 1),
                                        (4, 2), (5, 2),
                   (0, 5),                      (5, 3),
                                        (4, 4),
                                (3, 5), (4, 5), (5, 5)]
        for xy in self.segment:
            self.img.putpixel(xy, (0, 0, 0, 0))
        self.segmenter = ImageSegmenter(self.img)

    def test_get_rgba_matrix(self):
        copy = Image.new('RGBA', self.img.size)
        rgba_matrix = self.segmenter.get_rgba_matrix()

        for y in xrange(self.img.size[1]):
            for x in xrange(self.img.size[0]):
                copy.putpixel((x, y), (rgba_matrix[y][x]))

        self.assertItemsEqual(list(self.img.getdata()), list(copy.getdata()))

    def test_surrounding_pixels(self):
        self.assertItemsEqual(((1, 0), (0, 1)), self.segmenter.get_surrounding_pixels((0, 0)))

    def test_not_white(self):
        self.assertTrue(self.segmenter.is_not_white((2, 1)))

    def test_segment_image(self):
        segments = self.segmenter.segment_image(min_pixels=1)
        self.assertEqual(2, len(segments))
        self.assertItemsEqual([(2, 1), (3, 1), (4, 1), (5, 1), (5, 2), (4, 2), (5, 3)], segments[0].pix)
        self.assertItemsEqual([(4, 4), (4, 5), (3, 5), (5, 5)], segments[1].pix)

