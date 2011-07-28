# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.app.news.tests.SilvaNewsTestCase import NewsBaseTestCase


class NewsViewerTestCase(NewsBaseTestCase):
    """Test the NewsViewer interface.
    """
    def test_filters(self):
        self.assertEquals([self.root.newsfilter],
                          self.newsviewer.get_filters())
        self.newsviewer.set_filters([])
        self.assertEquals([], self.newsviewer.get_filters())

    def test_filters_reference_cleanup(self):
        self.assertEquals([self.root.newsfilter],
                        self.newsviewer.get_filters())
        self.root.manage_delObjects(['newsfilter'])
        self.assertEquals([], self.newsviewer.get_filters())

    def test_get_items(self):
        self.newsfilter.set_sources([self.source1])
        iops = [i.getPhysicalPath() for i in self.newsviewer.get_items()]
        self.assertTrue(('', 'root', 'source1', 'art1') in iops)
        self.assertTrue(('', 'root', 'source1', 'art2') in iops)
        self.assertEquals(2, len(iops))

        self.newsfilter.add_excluded_item(self.item1_2)
        iops = [i.getPhysicalPath() for i in self.newsviewer.get_items()]
        self.assertTrue(('', 'root', 'source1', 'art1') in iops)
        self.assertTrue(not ('', 'root', 'source1', 'art2') in iops)
        self.assertTrue(len(iops) == 1)


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsViewerTestCase))
    return suite
