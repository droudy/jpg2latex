# Copyright (C) 2018 Daniel Roudnitsky <droudnitsky@gmail.com>

"""
This module contains methods to classify the segments contained in an image using labeled data
"""

import os
import cPickle as pickle

from scipy.spatial.distance import euclidean

from segment_img import ImageSegmenter
from transform_segment import TransformSegment


def seg_and_classify_img(img_path, labels_dir):
    """
    Segment and classify the segments contained in an image

    Segment the image passed in. For each segment: transform it to the origin, rescale it to the size of the already
    labeled image vectors, convert the rescaled segment into a vector and compare against labeled vectors(lowest
    euclidean distance between the labeled vectors is the classification). The parameters to transform the segment are
    the same as those used to transform the labeled segments.

    :param img_path: path of image to classify
    :param labels_dir: path of directory containing serialized objects. Each object represents an image. The name of the
    object file is the label of the image and the object itself is a vector representing the image. All vectors should
    be of same length
    :return: List of `Segment` objects each with a classification attribute containing their classification
    """
    segments = ImageSegmenter(img_path).segment_image()
    labeled_segments = load_labeled_segments(labels_dir)
    for segment in segments:
        seg_transform = TransformSegment(segment)
        rescale_size, fill_val = load_size_and_fill_val(labels_dir)
        seg_transform.rescale(rescale_size)
        seg_vec = seg_transform.get_flattened_pix_grid(fill_val)
        classification = classify_segment_vector(seg_vec, labeled_segments)
        segment.classification = classification
    return segments


def classify_segment_vector(vec, labeled_segments):
    """
    Compare a vector that represents a segment against all labeled vectors in labeled_segments

    :param vec: Vector representing a segment that is to be classified
    :param labeled_segments: Dictionary where the keys are labels and values are vectors
    :return: Label of the labeled vector that has the smallest euclidean distance to the vec passed in
    """
    comparisons = []
    labels = labeled_segments.keys()
    labeled_vecs = labeled_segments.values()
    for i in xrange(len(labeled_segments)):
        comparisons.append((labels[i], euclidean(vec, labeled_vecs[i])))
    comparisons.sort(key=lambda x: x[1])
    return comparisons[0][0]


def load_labeled_segments(path_to_dir):
    """
    Deserialize all objects in path_to_dir. Each object in the dir represents an image. The name of the
    object file is the label of the image and the object itself is a vector representing the image. All vectors should
    be of same length. The keys of the dictionary are the labels and the values are their corresponding vectors that
    represent the labels
    """
    vec_dic = {}
    for file_path in os.listdir(path_to_dir):
        if file_path not in ['fill_val.p', 'size.p']:
            with open(os.path.join(path_to_dir, file_path), 'rb') as file_obj:
                vec_dic[file_path[:-2]] = pickle.load(file_obj)
    return vec_dic


def load_size_and_fill_val(path_to_dir):
    """
    Load the parameters used for `TransformSegment` when the labeled segments were initially serialized
    :return: tuple of size 2 containing (size, fill_val)
    """
    size_obj_file = open(os.path.join(path_to_dir, 'size.p'), 'rb')
    fill_val_obj_file = open(os.path.join(path_to_dir, 'fill_val.p'), 'rb')
    return pickle.load(size_obj_file), pickle.load(fill_val_obj_file)

