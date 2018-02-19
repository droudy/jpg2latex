# Copyright (C) 2018 Daniel Roudnitsky <droudnitsky@gmail.com>

import inspect
import os
import unittest

from classify_segments import seg_and_classify_img
from segments_to_latex import SegmentsToLatex


class TestSegmentsToLatex(unittest.TestCase):  # TODO add many more test cases

    def setUp(self):
        root_dir = os.path.dirname(inspect.getfile(seg_and_classify_img))
        self.test_images_dir = os.path.join(root_dir, 'test_images')
        self.labeled_dir = os.path.join(root_dir, 'serialized_labeled_imgs')

    def img_to_latex(self, img_name):
        img_path = os.path.join(self.test_images_dir, img_name)
        segments = seg_and_classify_img(img_path, self.labeled_dir)
        return SegmentsToLatex(segments).search_and_simplify((0, 0), (99999, 99999)).classification

    def test_image1(self):
        latex = self.img_to_latex('divisions.png')
        expected = '\\frac{\\sqrt{5 + 2} + \\frac{5}{2}}{4 0 0 0 0}'
        self.assertEqual(expected, latex)

    def test_image2(self):
        latex = self.img_to_latex('integral.png')
        expected = '\\int ( \\sqrt{x} + \\frac{1}{2 \\sqrt{x}} ) d x'
        self.assertEqual(expected, latex)

    def test_image3(self):
        latex = self.img_to_latex('nested_root.png')
        expected = '\\sqrt{5 + \\sqrt{5 + 1 0}}'
        self.assertEqual(expected, latex)

    def test_image4(self):
        latex = self.img_to_latex('root.png')
        expected = '5 + \\sqrt{5 + 1 0}'
        self.assertEqual(expected, latex)

    def test_image5(self):
        latex = self.img_to_latex('root_frac.png')
        expected = '\\frac{\\sqrt{5 + \\sqrt{5 + 1 0}}}{\\sqrt{4}}'
        self.assertEqual(expected, latex)

