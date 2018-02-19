# Copyright (C) 2018 Daniel Roudnitsky <droudnitsky@gmail.com>

"""
Compute the vector representations of labeled images/segments and serialize the vector objects so we don't needlessly
recompute the vector representations of the labeled data since they remains the same from run to run
"""

import os
import logging
import cPickle as pickle

from segment_img import ImageSegmenter
from transform_segment import TransformSegment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def serialize_imgs(dir_to_serialize, dir_to_place_objs, size, fill_val):
    """
    Vectorize all the labeled images in `dir_to_serialize` and save the vectors in the directory `dir_to_place_objs`

    :param dir_to_serialize: Directory containing labeled images to serialize
    :param dir_to_place_objs: Directory to place serialized objects into
    :param size: Resize parameter for creating vector representations
    :param fill_val: fill_val parameter for creating vector representations
    """
    logger.info("Parsing directory and vectorizing ...")
    vec_dic = search_dir_and_seg(dir_to_serialize, size, fill_val)
    labels = vec_dic.keys()
    vecs = vec_dic.values()

    for i in xrange(len(labels)):
        logger.info("Serializing %s ..." % labels[i])
        with open(os.path.join(dir_to_place_objs, labels[i] + '.p'), 'wb') as obj_file:
            pickle.dump(vecs[i], obj_file)

    size_obj_file = open(os.path.join(dir_to_place_objs, 'size.p'), 'wb')
    fill_val_obj_file = open(os.path.join(dir_to_place_objs, 'fill_val.p'), 'wb')

    pickle.dump(size, size_obj_file)
    pickle.dump(fill_val, fill_val_obj_file)
    fill_val_obj_file.close()
    size_obj_file.close()


def search_dir_and_seg(dir_path, resize, fill_val=-1):
    """
    Meant to be used on a folder with labeled segments to compare unknown examples against. All files
    in the folder should contain .png files with one segment in each image. This method searches the directory
    and creates a dictionary with each file name and the pixels in it that the segment comprises of.
    :return: Dictionary with the keys being labels and values being corresponding segments
    """
    vec_dic = {}
    for path in os.listdir(dir_path):
        if path[-4:] == '.png':
            segment = open_and_segment(dir_path + '/' + path)
            logger.info("Transofrming and vectorizing %s" % path)
            vec_dic[path[:-4]] = transform_and_vectorize(segment, resize, fill_val)
    return vec_dic


def open_and_segment(img_path):
    """
    To be used on images with only a single character/symbol/segment.
    :return list of pixels that segment comprises of
    """
    segments = ImageSegmenter(img_path).segment_image()
    if len(segments) != 1:
        raise ValueError("%s contains more than one segment" % img_path)
    return segments[0]


def transform_and_vectorize(segment, size, fill_val=-1):
    """
    Transform a segment to the origin, rescale it to size, and create flattened pixel grid
    filled with fill_val where there are white pixels
    """
    transform = TransformSegment(segment)
    transform.rescale(size)
    return transform.get_flattened_pix_grid(fill_val)


if __name__ == '__main__':
    folder = 'labeled'  # folder containing images to serialize
    serialized_folder = 'serialized_labeled_imgs'  # folder to place serialized objects representing the images
    size = (50, 50)  # size to resize images to
    fill_val = -1.45

    serialize_imgs(folder, serialized_folder, size, fill_val)

