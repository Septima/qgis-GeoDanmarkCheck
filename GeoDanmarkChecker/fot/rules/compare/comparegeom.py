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

from .comparerule import CompareRule
from ... import Repository
from ... import FeatureType
from ...geomutils.featurematcher import MatchFinder, ExactGeometryMatcher
from ...geomutils.segmentmatcher import SegmentMatchFinder
from qgis.core import QgsGeometry, QgsFeature


class MatchingGeometrySameDirection(CompareRule):
    """Check that matching 'before' and 'after' features effectively have the same direction.

    Takes both geometry direction and 'direction_attribute' into account. 'direction_attribute' has one of three
    values {null, 0, 1}. Where 1 indicates that the direction is reversed with respect to the actual geometry.
    If 'direction_attribute' is not present or it's value is null it is assumed to be 0.

    Parameters
    ----------
    name : str
        Name if this rule instance
    feature_type : fot.FeatureType
        Feature type to apply check to
    direction_attribute : str
        Attribute
    maxdist : float
        Maximum distance to consider geometries coincident.
    segmentize : float or None
        Segmentize geometry into pieces of maximum this length. If None the geometry is not segmentized.
    beforefilter : str
        QGIS Filter Expression which is applied to 'before' features before evaluating this rule.
    afterfilter : str
        QGIS Filter Expression which is applied to 'after' features before evaluating this rule.
    """
    def __init__(self, name, feature_type, direction_attribute, maxdist, segmentize = None, beforefilter=None, afterfilter=None):
        super(MatchingGeometrySameDirection, self).__init__(name, beforefilter, afterfilter)
        if not isinstance(feature_type, FeatureType):
            raise TypeError()
        self.featuretype = feature_type
        self.direction_attribute = direction_attribute
        self.maxdist = float(maxdist)
        self.segmentize = float(segmentize) if segmentize else 0

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        beforefeats = beforerepo.read(self.featuretype, attributes=[self.direction_attribute], feature_filter=self.beforefilter)
        afterfeats = afterrepo.read(self.featuretype, attributes=[self.direction_attribute], feature_filter=self.afterfilter)

        # Features that appear to be changed
        changed_before_features = list(beforefeats)
        changed_after_features = []

        progressreporter.begintask(self.name, len(afterfeats))

        exact_matcher = ExactGeometryMatcher()

        # Find exact geometry matches
        finder = MatchFinder(beforefeats)
        for f in afterfeats:
            matches = finder.findmatching(f, exact_matcher)
            match_found = False
            for match in matches:
                match_found = True
                self._check(errorreporter, match.feature2, f, f, True, False)
                # Remove from changed if exists (Duplicate geometries forces us to use this check)
                if match.feature2 in changed_before_features:
                    changed_before_features.remove(match.feature2)
            if match_found: continue
            # check on reversed geom
            reversed_geom = QgsGeometry.fromPolyline(list(reversed(f.geometry().asPolyline())))
            matches = finder.findmatching(reversed_geom, exact_matcher)
            for match in matches:
                match_found = True
                self._check(errorreporter, match.feature2, f, f, False, False)
                # Remove from changed if exists (Duplicate geometries forces us to use this check)
                if match.feature2 in changed_before_features:
                    changed_before_features.remove(match.feature2)
            if not match_found:
                changed_after_features.append(f)
            progressreporter.completed_one()

        # Compare nonexact geometry matches
        progressreporter.begintask(self.name, len(changed_after_features))
        segmentmatchfinder = SegmentMatchFinder(changed_before_features, segmentize=self.segmentize)
        segmentmatchfinder2 = SegmentMatchFinder(afterfeats, segmentize=self.segmentize)
        for f in changed_after_features:
            for sm in segmentmatchfinder.findmatching(f, maxdistance=self.maxdist):
                f2 = sm.nearestfeature
                # check so that the projection of sm at least once matches the same nearest feature when segment matched against afterfeats
                projgeom = sm.toprojgeometry()
                projmatches = False
                for sm2 in segmentmatchfinder2.findmatching(projgeom, maxdistance=self.maxdist, ignore=f):
                    projmatches = True
                    if f2 == sm2.nearestfeature:
                        self._check(errorreporter, f2, f, sm.togeometry(), sm.samedirection(), True)
                        break
                if not projmatches:
                    self._check(errorreporter, f2, f, sm.togeometry(), sm.samedirection(), True)
            progressreporter.completed_one()

    # check for exact geometry matches - should have same dir
    def _check(self, errorreporter, fbefore, fafter, geom, same_direction, is_segment):
        messages = []
        before_dir = fbefore[self.direction_attribute] if fbefore.fieldNameIndex(self.direction_attribute) != -1 else 0
        after_dir = fafter[self.direction_attribute] if fafter.fieldNameIndex(self.direction_attribute) != -1 else 0

        direction_match = before_dir != after_dir if same_direction else before_dir == after_dir

        segment_text = " segment" if is_segment else ""

        if direction_match:
            messages.append(u'{0}: "{1}" -> "{2}"'.format(self.direction_attribute, before_dir, after_dir))
        if messages:
            if same_direction:
                message = "Geometry" + segment_text + " match, attribute changed: " + '; '.join(messages)
            else:
                message = "Geometry" + segment_text + " reversed match, attribute unchanged: " + '; '.join(messages)
            errorreporter.error(self.name, self.featuretype, message, geom)
