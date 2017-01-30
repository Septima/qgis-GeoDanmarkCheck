# coding=utf-8

import unittest

from qgis.core import QgsGeometry
from qgis.core import QgsFeature
from ...fot.geomutils.segmentmatcher import SegmentMatchFinder


class TestIssue45(unittest.TestCase):
    a = QgsFeature()
    b = QgsFeature()
    c = QgsFeature()
    features = [a, b]

    def test_should_not_match_new_against_old_when_old_has_closer_match(self):
        self.a.setGeometry(QgsGeometry.fromWkt("LINESTRING (0 0, 50 0)"))
        self.b.setGeometry(QgsGeometry.fromWkt("LINESTRING (50 0, 100 0)"))
        self.c.setGeometry(QgsGeometry.fromWkt("LINESTRING (0 20, 50 0)"))

        smf = SegmentMatchFinder(self.features, segmentize=5)
        matches = smf.findmatching(self.c, maxdistance=10)

        self.assertEqual(len(matches), 1)

    def test_should_not_match_new_against_old_when_old_has_closer_match_real_data(self):
        self.a.setGeometry(QgsGeometry.fromWkt("LineStringZ (581187.19999999995343387 6386157.0400000000372529 14.27999999999999936, 581131.69999999995343387 6386156.99000000022351742 14.21000000000000085, 581119.56000000005587935 6386153.88999999966472387 14.84999999999999964, 581114.59999999997671694 6386152.69000000040978193 14.8100000000000005, 581012.86999999999534339 6386147.36000000033527613 14.34999999999999964, 580975.90000000002328306 6386141.28000000026077032 14.58999999999999986, 580972.23999999999068677 6386140.61000000033527613 14.59999999999999964, 580961.13000000000465661 6386110.54999999981373549 14.65000000000000036, 580951.16000000003259629 6386103.36000000033527613 14.66000000000000014, 580944.60999999998603016 6386103.42999999970197678 14.66000000000000014, 580878.93999999994412065 6386106.30999999959021807 14.67999999999999972, 580879.26000000000931323 6386082.44000000040978193 14.86999999999999922, 580881.0400000000372529 6386048.12000000011175871 14.58000000000000007, 580881.93999999994412065 6386034.33999999985098839 14.44999999999999929, 580886.68000000005122274 6386020.38999999966472387 14.39000000000000057, 580882.39000000001396984 6386013.44000000040978193 14.39000000000000057, 580883.51000000000931323 6385974.88999999966472387 14.30000000000000071, 580886.36999999999534339 6385962.49000000022351742 13.80000000000000071)"))
        self.b.setGeometry(QgsGeometry.fromWkt("LineStringZ (581187.19999999995343387 6386157.0400000000372529 14.27999999999999936, 581249.47999999998137355 6386157.11000000033527613 14.35999999999999943, 581347.90000000002328306 6386158.2099999999627471 14.5)"))
        self.c.setGeometry(QgsGeometry.fromWkt("LineStringZ (581164.43000000005122274 6386133.36000000033527613 15.24000000000000021, 581183.40000000002328306 6386153.58999999985098839 15.13000000000000078, 581187.19999999995343387 6386157.0400000000372529 14.27999999999999936)"))

        smf = SegmentMatchFinder(self.features, segmentize=5)
        matches = smf.findmatching(self.c, maxdistance=10)

        self.assertEqual(len(matches), 1)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestIssue45)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
