# Copyright (C) 2018 Daniel Roudnitsky <droudnitsky@gmail.com>

from classify_segments import seg_and_classify_img
from segments_to_latex import SegmentsToLatex


def image_to_latex(img_path):
    """
    Segment an image, classify the segments, and deduce its latex code from the classified segments
    """
    classified_segments = seg_and_classify_img(img_path, 'serialized_labeled_imgs')
    seg_to_latex = SegmentsToLatex(classified_segments)
    simplfied = seg_to_latex.search_and_simplify((0, 0), (999999, 999999))  # search entire region
    return simplfied.classification
