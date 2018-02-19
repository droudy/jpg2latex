# Copyright (C) 2018 Daniel Roudnitsky <droudnitsky@gmail.com>

import inspect
import os
import unittest

from classify_segments import seg_and_classify_img


class TestClassifier(unittest.TestCase):  # TODO add many more test cases

    def setUp(self):
        root_dir = os.path.dirname(inspect.getfile(seg_and_classify_img))
        self.test_images_dir = os.path.join(root_dir, 'test_images')
        self.labeled_dir = os.path.join(root_dir, 'serialized_labeled_imgs')

    def classify(self, img_name):
        img_path = os.path.join(self.test_images_dir, img_name)
        segments = seg_and_classify_img(img_path, self.labeled_dir)
        return [segment.classification for segment in segments]

    def test_image1(self):
        classifications = self.classify('divisions.png')
        expected = ['5', 'radical', '5', '2', '+', '+', 'division', '2', 'division', '4', '0', '0', '0', '0']
        self.assertItemsEqual(expected, classifications)

    def test_image2(self):
        classifications = self.classify('integral.png')
        expected = ['1', 'integral', 'radical', '(', ')', 'd', '+', 'x', 'x', 'division', 'radical', '2', 'x']
        self.assertItemsEqual(expected, classifications)

    def test_image3(self):
        classifications = self.classify('latex2.png')
        expected = ['b', '2', 'd', 'integral', 'v', 'u', 'division', '2', 'd', 'x', 'a']
        self.assertItemsEqual(expected, classifications)

    def test_image4(self):
        classifications = self.classify('nested_root.png')
        expected = ['radical', 'radical', '5', '5', '1', '0', '+', '+']
        self.assertItemsEqual(expected, classifications)

    def test_image5(self):
        classifications = self.classify('root_frac.png')
        expected = ['radical', 'radical', '1', '0', '5', '5', '+', '+', 'division', 'radical', '4']
        self.assertItemsEqual(expected, classifications)
