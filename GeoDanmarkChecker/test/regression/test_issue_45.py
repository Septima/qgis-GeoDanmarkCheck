# coding=utf-8

import unittest

from qgis.core import QgsGeometry
from qgis.core import QgsFeature
from ...fot.geomutils.segmentmatcher import SegmentMatchFinder


class TestIssue45(unittest.TestCase):
    def test_should_not_match_new_against_old_when_old_has_closer_match(self):
        a = QgsFeature()
        b = QgsFeature()
        c = QgsFeature()
        d = QgsFeature()
        a.setGeometry(QgsGeometry.fromWkt("LINESTRING (0 0, 50 0)"))
        b.setGeometry(QgsGeometry.fromWkt("LINESTRING (50 0, 100 0)"))
        c.setGeometry(QgsGeometry.fromWkt("LINESTRING (0 20, 50 0)"))
        d.setGeometry(QgsGeometry.fromWkt("LINESTRING (0 0, 50 0)"))
        features = [a, b]

        osmf = SegmentMatchFinder(features, segmentize=5)
        om = osmf.findmatching(c, maxdistance=10)
        self.assertEqual(len(om), 1)

        projgeom = om[0].toprojgeometry()
        #print projgeom.exportToWkt()

        nsmf = SegmentMatchFinder([c, d], segmentize=5)
        nm = nsmf.findmatching(projgeom, maxdistance=10)
        self.assertEqual(len(nm), 1)

        self.assertNotEqual(om[0].nearestfeature, nm[0].nearestfeature)

    def test_should_not_match_new_against_old_when_old_has_closer_match_real_data(self):
        of1 = QgsFeature()
        of2 = QgsFeature()
        of3 = QgsFeature()

        nf1 = QgsFeature()
        nf2 = QgsFeature()
        nf3 = QgsFeature()
        nf4 = QgsFeature()

        of1.setGeometry(QgsGeometry.fromWkt("LineStringZ (581187.19999999995343387 6386157.0400000000372529 14.27999999999999936, 581131.69999999995343387 6386156.99000000022351742 14.21000000000000085, 581119.56000000005587935 6386153.88999999966472387 14.84999999999999964, 581114.59999999997671694 6386152.69000000040978193 14.8100000000000005, 581012.86999999999534339 6386147.36000000033527613 14.34999999999999964, 580975.90000000002328306 6386141.28000000026077032 14.58999999999999986, 580972.23999999999068677 6386140.61000000033527613 14.59999999999999964, 580961.13000000000465661 6386110.54999999981373549 14.65000000000000036, 580951.16000000003259629 6386103.36000000033527613 14.66000000000000014, 580944.60999999998603016 6386103.42999999970197678 14.66000000000000014, 580878.93999999994412065 6386106.30999999959021807 14.67999999999999972, 580879.26000000000931323 6386082.44000000040978193 14.86999999999999922, 580881.0400000000372529 6386048.12000000011175871 14.58000000000000007, 580881.93999999994412065 6386034.33999999985098839 14.44999999999999929, 580886.68000000005122274 6386020.38999999966472387 14.39000000000000057, 580882.39000000001396984 6386013.44000000040978193 14.39000000000000057, 580883.51000000000931323 6385974.88999999966472387 14.30000000000000071, 580886.36999999999534339 6385962.49000000022351742 13.80000000000000071)"))
        of2.setGeometry(QgsGeometry.fromWkt("LineStringZ (581187.19999999995343387 6386157.0400000000372529 14.27999999999999936, 581249.47999999998137355 6386157.11000000033527613 14.35999999999999943, 581347.90000000002328306 6386158.2099999999627471 14.5)"))
        of3.setGeometry(QgsGeometry.fromWkt("LineStringZ (581187.19999999995343387 6386157.0400000000372529 14.27999999999999936, 581188.21999999997206032 6386193.41999999992549419 14.52999999999999936, 581245.40000000002328306 6386194.08000000007450581 14.33999999999999986, 581305.42000000004190952 6386194.40000000037252903 14.55000000000000071, 581322.48999999999068677 6386194.84999999962747097 14.67999999999999972)"))
        ofs = [of1, of2, of3]

        nf1.setGeometry(QgsGeometry.fromWkt("LineStringZ (581187.19999999995343387 6386157.0400000000372529 14.27999999999999936, 581132.56000000005587935 6386156.30999999959021807 14.21000000000000085, 581120.42000000004190952 6386153.2099999999627471 14.84999999999999964, 581115.4599999999627471 6386152.00999999977648258 14.8100000000000005, 581013.72999999998137355 6386146.67999999970197678 14.34999999999999964, 580976.76000000000931323 6386140.59999999962747097 14.58999999999999986, 580973.09999999997671694 6386139.92999999970197678 14.59999999999999964, 580966.06999999994877726 6386122.91999999992549419 14.63000000000000078, 580961.98999999999068677 6386109.87000000011175871 14.65000000000000036, 580952.02000000001862645 6386102.67999999970197678 14.66000000000000014, 580945.46999999997206032 6386102.75 14.66000000000000014, 580911.72999999998137355 6386105.08000000007450581 14.66999999999999993, 580901.31000000005587935 6386105.67999999970197678 14.67999999999999972, 580896.33999999996740371 6386106.29999999981373549 14.69999999999999929, 580892.9599999999627471 6386106.30999999959021807 14.71000000000000085, 580889.84999999997671694 6386104.96999999973922968 14.71000000000000085, 580886.09999999997671694 6386103.92999999970197678 14.72000000000000064, 580882.66000000003259629 6386103.46999999973922968 14.72000000000000064, 580881.67000000004190952 6386100.87000000011175871 14.72000000000000064, 580881.27000000001862645 6386098.13999999966472387 14.73000000000000043, 580878.52000000001862645 6386094.4599999999627471 14.74000000000000021, 580877.05000000004656613 6386090.70000000018626451 14.74000000000000021, 580878.25 6386086.13999999966472387 14.75, 580879.5400000000372529 6386074.42999999970197678 14.86999999999999922, 580881.31999999994877726 6386040.11000000033527613 14.58000000000000007, 580882.80000000004656613 6386033.66000000014901161 14.44999999999999929, 580884.83999999996740371 6386020.58999999985098839 14.39000000000000057, 580883.25 6386012.75999999977648258 14.39000000000000057, 580883.5 6385974.08999999985098839 14.30000000000000071, 580886.36999999999534339 6385962.49000000022351742 13.80000000000000071)"))
        nf2.setGeometry(QgsGeometry.fromWkt("LineStringZ (581187.19999999995343387 6386157.0400000000372529 14.27999999999999936, 581249.47999999998137355 6386157.11000000033527613 14.35999999999999943, 581347.90000000002328306 6386158.2099999999627471 14.5)"))
        nf3.setGeometry(QgsGeometry.fromWkt("LineStringZ (581187.19999999995343387 6386157.0400000000372529 14.27999999999999936, 581188.21999999997206032 6386193.41999999992549419 14.52999999999999936, 581245.40000000002328306 6386194.08000000007450581 14.33999999999999986, 581305.42000000004190952 6386194.40000000037252903 14.55000000000000071, 581322.48999999999068677 6386194.84999999962747097 14.67999999999999972)"))
        nf4.setGeometry(QgsGeometry.fromWkt("LineStringZ (581164.43000000005122274 6386133.36000000033527613 15.24000000000000021, 581183.40000000002328306 6386153.58999999985098839 15.13000000000000078, 581187.19999999995343387 6386157.0400000000372529 14.27999999999999936)"))
        nfs = [nf1, nf2, nf3, nf4]

        osmf = SegmentMatchFinder(ofs, segmentize=5)
        om = osmf.findmatching(nf4, maxdistance=10)
        self.assertEqual(len(om), 1)

        projgeom = om[0].toprojgeometry()
        #print projgeom.exportToWkt()

        nsmf = SegmentMatchFinder(nfs, segmentize=5)
        nm = nsmf.findmatching(projgeom, maxdistance=10)
        self.assertEqual(len(nm), 1)

        self.assertNotEqual(om[0].nearestfeature, nm[0].nearestfeature)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestIssue45)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
