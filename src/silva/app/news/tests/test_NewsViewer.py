# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject

from silva.app.news.interfaces import INewsViewer
from silva.app.news.tests.SilvaNewsTestCase import NewsBaseTestCase


class NewsViewerTestCase(NewsBaseTestCase):
    """Test the NewsViewer interface.
    """

    def test_implementation(self):
        self.assertTrue(verifyObject(INewsViewer, self.root.viewer))

    def test_filters_add(self):
        self.assertEqual([self.root.filter1], self.root.viewer.get_filters())
        self.root.viewer.add_filter(self.root.filter2)
        self.assertItemsEqual(
            [self.root.filter1, self.root.filter2],
            self.root.viewer.get_filters())

    def test_filters_set(self):
        self.assertEqual([self.root.filter1], self.root.viewer.get_filters())
        self.root.viewer.set_filters([])
        self.assertEqual([], self.root.viewer.get_filters())

    def test_filters_delete(self):
        self.assertEquals([self.root.filter1], self.root.viewer.get_filters())
        self.root.manage_delObjects(['filter1'])
        self.assertEquals([], self.root.viewer.get_filters())

    def test_get_items(self):
        self.root.filter1.set_sources([self.root.source1])
        self.assertItemsEqual(
            ['/root/source1/art1/0', '/root/source1/art2/0'],
            [b.getPath() for b in self.root.viewer.get_items()])

    def test_get_items_filtered(self):
        self.root.filter1.set_sources([self.root.source1])
        self.root.filter1.add_excluded_item(self.root.source1.art2)
        self.assertEqual(
            ['/root/source1/art1/0'],
            [b.getPath() for b in self.root.viewer.get_items()])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsViewerTestCase))
    return suite
