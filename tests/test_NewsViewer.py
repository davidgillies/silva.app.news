# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaNews.tests.SilvaNewsTestCase import NewsBaseTestCase


class NewsViewerTestCase(NewsBaseTestCase):
    """Test the NewsViewer interface.
    """
    def test_filters(self):
        self.assert_(self.newsviewer.filters() == ['/root/newsfilter'])
        self.newsviewer.set_filters([])
        self.assert_(self.newsviewer.filters() == [])

    def test_findfilters(self):
        self.assert_(self.newsviewer.findfilters() == ['/root/newsfilter'])

    def test_findfilters_pairs(self):
        self.assert_(self.newsviewer.findfilters_pairs() == [
                (u'NewsFilter (<a href="/root/newsfilter/edit">'
                 u'/root/newsfilter</a>)',
                 '/root/newsfilter')])

    def test_verify_filters(self):
        self.assert_(self.newsviewer.filters() == ['/root/newsfilter'])
        self.root.manage_delObjects('newsfilter')
        self.assert_(self.newsviewer.filters() == [])

    def test_get_items(self):
        self.newsfilter.add_source('/root/source1',1)
        iops = [i.object_path for i in self.newsviewer.get_items()]
        self.assert_(('', 'root', 'source1', 'art1') in iops)
        self.assert_(('', 'root', 'source1', 'art2') in iops)
        self.assert_(len(iops) == 2)

        self.newsfilter.set_excluded_item(('', 'root', 'source1', 'art2'), 1)
        iops = [i.object_path for i in self.newsviewer.get_items()]
        self.assert_(('', 'root', 'source1', 'art1') in iops)
        self.assert_(not ('', 'root', 'source1', 'art2') in iops)
        self.assert_(len(iops) == 1)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsViewerTestCase))
    return suite
