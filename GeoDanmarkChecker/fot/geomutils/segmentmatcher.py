# -*- coding: utf-8 -*-
"""
Routines for quality control of GeoDanmark map data
Copyright (C) 2016
Developed by Septima.dk for the Danish Agency for Data Supply and Efficiency

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from qgis.core import QgsGeometry
from . import FeatureIndex
from featurematcher import FeatureMatch
from . import togeometry, tocoordinates
from .algorithms import densify, line_locate_point
from math import sqrt, cos, pi

class SegmentMatch(object):
    def __init__(self, f, nearest_feature):
        self.thisfeature = f
        self.nearestfeature = nearest_feature
        self.vertices = []
        self.match_prev_distances = []
        self.match_this_distances = []
        self.maxdistancefound = -1

    def togeometry(self):
        return QgsGeometry.fromPolyline(self.vertices)

    def addvertex(self, point, distance, match_prev_distance, match_this_distance):
        self.vertices.append(point)
        self.match_prev_distances.append(match_prev_distance)
        self.match_this_distances.append(match_this_distance)
        self.maxdistancefound = max(distance, self.maxdistancefound)

    def sameDirection(self):
        same_direction = True
        for i in xrange(0, len(self.vertices)):
            prev_distance = self.match_prev_distances[i]
            this_distance = self.match_this_distances[i]
            prev_point = prev_distance[1]
            prev_index = prev_distance[2]
            this_point = this_distance[1]
            this_index = this_distance[2]
            if prev_index > this_index:
                same_direction = False
            elif prev_index == this_index:
                 vertex = self.nearestfeature.geometry().vertexAt(prev_index)
                 if prev_point.sqrDist(vertex) < this_point.sqrDist(vertex):
                     same_direction = False
        return same_direction

class SegmentMatchFinder(object):
    def __init__(self, matchagainstfeatures, segmentize=0):
        self.features = matchagainstfeatures
        self.indexedfeatures = FeatureIndex(matchagainstfeatures, usespatialindex=True)
        self.segmentize = float(segmentize) if segmentize else 0
        self.approximate_angle_threshold = 1/cos(pi/4.0)

    def findmatching(self, feature, maxdistance):
        maxdistance = float(maxdistance)
        maxdistsqrd = maxdistance * maxdistance
        geom = togeometry(feature)

        # segmentize feature
        seggeom = densify(geom, self.segmentize) if self.segmentize else geom
        segcoords = tocoordinates(seggeom)

        # For each vertws in this geom calculate distance to all neighbors
        distances_per_vertex = []
        for coord in segcoords:
            rect = QgsGeometry.fromPoint(coord).boundingBox()
            rect.buffer(maxdistance)
            nearbyfeatures = self.indexedfeatures.geometryintersects(rect)
            distances = {}
            for neighbor in nearbyfeatures:
                # Dont match self
                if neighbor != feature:
                    sqrddist, closestsegmentpoint, indexofclosestvertexafter = neighbor.geometry().closestSegmentWithContext(coord)
                    if sqrddist <= maxdistsqrd:
                        distances[neighbor] = (sqrddist, closestsegmentpoint, indexofclosestvertexafter)
            distances_per_vertex.append(distances)

        # for each segment find the matching feature which has the lowest summed sqrdistance from the endpoints
        # Make sure we dont use distance to the same point
        segment_matches = []
        current_segmentmatch = None
        match_prev_distance = None
        match_this_distance = None
        for i in range(1, len(distances_per_vertex)):
            this_vertex = segcoords[i]
            prev_vertex = segcoords[i-1]
            this_segment = QgsGeometry.fromPolyline([prev_vertex, this_vertex])
            this_segment_length = this_segment.length()
            prev_distances = distances_per_vertex[i - 1]
            this_distances = distances_per_vertex[i]
            smallest_distance_sqrd = float('inf')
            smallest_distance_feature = None
            for f, this_distance in this_distances.iteritems():
                if not f in prev_distances:
                    # Feature f wasnt nearby at the previous vertex => f is not candidate for this segment
                    continue
                prev_distance = prev_distances[f]
                sumsqrddistance = this_distance[0] + prev_distance[0]
                # What point was closest? Make sure we dont match an endpoint of the other geom or a geom at a near 90 angle
                prev_point = prev_distance[1]
                this_point = this_distance[1]
                d1 = line_locate_point(f.geometry(), prev_point)
                d2 = line_locate_point(f.geometry(), this_point)
                other_segment_length = abs(d1 - d2)
                if other_segment_length < this_segment_length * self.approximate_angle_threshold and sumsqrddistance < smallest_distance_sqrd:
                    # We found a closer feature
                    smallest_distance_sqrd = sumsqrddistance
                    smallest_distance_feature = f
                    match_prev_distance = prev_distance
                    match_this_distance = this_distance
                    # Perfekt match. Stop looking
                    if smallest_distance_sqrd == 0.0:
                        break
            # Do we have a running segmentmatch to extend?
            if current_segmentmatch and current_segmentmatch.nearestfeature == smallest_distance_feature:
                current_segmentmatch.addvertex(this_vertex, sqrt(smallest_distance_sqrd), match_prev_distance, match_this_distance)
            else:
                # The closes feature is not the same as in the last segment
                if current_segmentmatch:
                    segment_matches.append(current_segmentmatch)
                    current_segmentmatch = None
                if smallest_distance_feature:
                    current_segmentmatch = SegmentMatch(feature, smallest_distance_feature)
                    current_segmentmatch.addvertex(prev_vertex, sqrt(smallest_distance_sqrd), match_prev_distance, match_this_distance)
                    current_segmentmatch.addvertex(this_vertex, sqrt(smallest_distance_sqrd), match_prev_distance, match_this_distance)
        # Add last segmentmatch
        if current_segmentmatch:
            segment_matches.append(current_segmentmatch)
        return segment_matches