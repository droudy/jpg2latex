# Copyright (C) 2018 Daniel Roudnitsky <droudnitsky@gmail.com>

"""
Given a list of characters such as (5, 3, division_sign) and their corresponding coordinates ((51,86), (45,250), (46,125))
deduce what latex source code would generate such characters in those positions
"""


class SegmentsToLatex(object):
    """
    Deduce a latex representation of a list of `Segment` objects (can be numbers, letters, symbols, etc.) based on the
    relative position and size of the segments
    """

    def __init__(self, segments):
        """
        :param segments: List of `Segment` objects which together represent an equation/expression
        """
        self.segs = segments

    def search_region(self, upper_left, lower_right, ignore=None):
        """
        Search a rectangular region bounded by the coordinates `upper_left` and `lower_right`

        :param upper_left: Upper left coordinate of the search region
        :param lower_right: Lower right coordinate of the search region
        :param ignore: Object to ignore if found in the search region
        :return: List of segment objects whose centroid is in that region
        """
        results = []
        for segment in self.segs:
            if upper_left[0] < segment.centroid[0] < lower_right[0] and \
               upper_left[1] < segment.centroid[1] < lower_right[1]:

                # the centroid of a radical outside the search region can lie inside the region, so check to make
                # sure that in the case of a radical its actually inside the search region
                if segment.classification == 'radical':
                    radical_area = self.get_area(segment.upper_left, segment.lower_right)
                    region_area = self.get_area(upper_left, lower_right)
                    if radical_area > region_area:
                        continue

                if ignore is not None:
                    if segment != ignore:
                        results.append(segment)
                else:
                    results.append(segment)
        return results

    def search_and_simplify(self, upper_left, lower_right, ignore=None):
        """
        Searches a region and will also search any sub regions nested in that region. Sub-regions are defined by segments
        that are special operators(operators like division or radicals with special behavior/formatting). When there are
        no special operators in a region/sub-region all segments in that region are simplified(combined into one
        `CombinedSegments` object whose classification is the latex code that corresponds to the segments in that region)
         and the `CombinedSegments` object is returned

        For example a division sign will have a sub-region `top_region` above the division sign to be searched and
        a sub-region `bottom_region` below the division sign that needs to be searched. `search_and_simplify(top_region)` is
        called and simplifies all `Segment` objects(including special operators) in top_region into one `CombinedSegments`
        object whose `classification` attribute contains the latex that describes all the `Segment` objects that were
        inside of top_region. The same is done for `bottom_region`. The result is that the division sign `Segment` object
        will now have one `CombinedSegments` object above it(combined_above) and one below it(combined_below) and we can
        now easily combine the three into one object with the classification:
        "/frac{combined_above.classification}{combined_below.classification}"

        :param upper_left: Upper left coordinate of the search region
        :param lower_right: Lower right coordinate of the search region
        :param ignore: Object to ignore if found in the search region
        :return: A `CombinedSegments` object that represents all objects found in the search region
        """
        to_search = self.search_region(upper_left, lower_right, ignore)
        while self.contains_special_op(to_search):
            if self.contains_op(to_search, 'division'):
                division = self.get_longest_division(to_search)
                SpecialOperators.division(self, division, upper_left, lower_right)
            elif self.contains_op(to_search, 'radical'):
                radical = self.get_op(to_search, 'radical')
                SpecialOperators.radical(self, radical)
            elif self.contains_op(to_search, 'integral'):
                integral = self.get_op(to_search, 'integral')
                integral.classification = '\\int'
            else:
                raise ValueError('you fucked up')
            to_search = self.search_region(upper_left, lower_right, ignore)
        return self.simplify(to_search)

    def contains_special_op(self, segments):
        """
        Return true if a segment in `segments` is an operator with special behavior
        """
        for op in ['division', 'integral', 'radical']:
            if self.contains_op(segments, op):
                return True
        return False

    def contains_op(self, segments, op_name):
        """
        Return true if a segment in 'segments' is of classification `op_name`
        """
        try:
            self.get_op(segments, op_name)
            return True
        except ValueError:
            return False

    def get_op(self, segments, op):
        """
        Return first segment object of classification `op`. Method should only be called if segments is known to contain
        that op
        """
        for seg in segments:
            if seg.classification == op:
                return seg
        raise ValueError('%s not found in segments passed in' % op)

    def get_longest_division(self, segments):
        """
        Return longest division sign found in segments (the one that should be simplified first)
        """
        divisions = [seg for seg in segments if seg.classification == 'division']
        if len(divisions) == 0:
            return None
        else:
            return sorted(divisions, key=lambda seg: seg.dimensions[0], reverse=True)[0]

    def simplify(self, segments):
        """
        Simplifies a list of segments by combining them based on position from leftmost to rightmost. Should not be used
        with any unsimplified/uncombined special operators
        :return: `CombinedSegments` object
        """
        in_order = sorted(segments, key=lambda x: x.centroid[0])  # store from left to right based on x value of centroids
        combined_name = ' '.join([seg.classification for seg in in_order])
        return self.combine_segments(segments, combined_name)

    def combine_segments(self, segments, classification):
        """
        Combine `Segment` objects together into one `CombinedSegments` object

        For example if you segmented an image of the equation "3+5" you would have three `Segment` objects representing
        3, +, and 5 respectively. They can be combined logically into one `CombinedSegments` objects with the
        classification "3+5" which represents the expression in one object instead of three

        :param segments: list of segments to combine into one
        :param classification: classification of the combined segments
        :return: `CombinedSegments` object
        """

        class CombinedSegments(object):
            """
            Data structure that represents a group of segments that are combined into one object under one
            name/classification. Similar to `Segment` data structure but without attributes that aren't needed anymore
            """

            def __init__(self, classification, centroid):
                self.classification = classification
                self.centroid = centroid

        sum_x, sum_y = 0.0, 0.0
        for segment in segments:
            self.segs.remove(segment)
            sum_x += segment.centroid[0]
            sum_y += segment.centroid[1]
        combined_centroid = sum_x / len(segments), sum_y / len(segments)
        combined_segment = CombinedSegments(classification, combined_centroid)
        self.segs.append(combined_segment)
        return combined_segment

    def get_area(self, upper_left_coord, lower_right_coord):
        """
        Return area of the rectangular region bounded by `upper_left_coord` and `lower_right_coord`
        """
        width = lower_right_coord[0] - upper_left_coord[0]
        height = lower_right_coord[1] - upper_left_coord[1]
        return width * height


class SpecialOperators(object):
    """
    The `SpecialOperators` class defines the behavior of special operators (what sub-regions to search for a given
    special operator and how to combine the results of the sub-region search for that operator)
    """

    @staticmethod
    def radical(instance, operator):
        """
        Just evaluate everything inside the root. TODO search for nth root
        """
        bounds = (operator.upper_left, operator.lower_right)
        nested = instance.search_and_simplify(bounds[0], bounds[1], ignore=operator)
        latex = '\\sqrt{%s}' % nested.classification
        return instance.combine_segments([operator, nested], latex)

    @staticmethod
    def division(instance, operator, upper_left, lower_right):
        """
        Search above and below the division sign
        """
        upper_y_bound = upper_left[1]
        lower_y_bound = lower_right[1]

        num_upper_left = operator.upper_left[0], upper_y_bound
        num_lower_right = operator.lower_right[0], operator.upper_left[1]
        numerator = instance.search_and_simplify(num_upper_left, num_lower_right)

        denom_upper_left = operator.upper_left[0], operator.lower_right[1]
        denom_lower_right = operator.lower_right[0], lower_y_bound
        denominator = instance.search_and_simplify(denom_upper_left, denom_lower_right)

        latex = '\\frac{%s}{%s}' % (numerator.classification, denominator.classification)
        return instance.combine_segments([operator, numerator, denominator], latex)

