# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from DateTime import DateTime

from zope.interface.verify import verifyObject

from silva.app.news.interfaces import INewsFilter
from silva.app.news.testing import FunctionalLayer


class NewsFilterTestCase(unittest.TestCase):
    """Test the NewsFilter interface.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_filter(self):
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsFilter('news_filter', 'News Filter')
        news_filter = self.root._getOb('news_filter', None)
        self.assertTrue(verifyObject(INewsFilter, news_filter))


class SourcesNewsFilterTestCase(unittest.TestCase):
    """Test the NewsFilter content.
    """
    layer = FunctionalLayer


    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News')
        factory.manage_addNewsPublication('events', 'Events')
        factory.manage_addNewsFilter('news_filter', 'Filter')

        factory = self.root.news.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('article1', 'First Article')
        factory.manage_addNewsItem('article2', 'Second Article')
        factory.manage_addNewsItem('article3', 'Third Article')

    def test_sources(self):
        news_filter = self.root.news_filter
        self.assertItemsEqual(
            news_filter.get_sources(),
            [])

        news_filter.set_sources([self.root.news, self.root.events])
        self.assertItemsEqual(
            news_filter.get_sources(),
            [self.root.news, self.root.events])

        self.root.manage_delObjects(['events'])
        self.assertItemsEqual(
            news_filter.get_sources(),
            [self.root.news])

    def test_items(self):
        self.newsfilter.set_subjects(['sub'])
        self.newsfilter.set_target_audiences(['ta'])
        self.newsfilter.set_sources([self.source1])
        res = self.newsfilter.get_all_items()
        pps = ['/'.join(i.getPhysicalPath()) for i in res]
        self.assertTrue('/root/source1/art1' in pps)
        self.assertTrue(not '/root/source1/art2' in pps)
        self.assertTrue(not '/root/source1/somefolder/art3' in pps)
        self.assertEquals(1, len(pps))
        self.newsfilter.add_excluded_item(self.item1_1)
        self.assertEquals(1, len(self.newsfilter.get_excluded_items()))
        self.assertEquals([], self.newsfilter.get_last_items(10))

    def test_search_items(self):
        self.newsfilter.set_subjects(['sub'])
        self.newsfilter.set_target_audiences(['ta'])
        self.newsfilter.set_sources([self.source1, self.source2, self.source3])
        resids = [i.id for i in self.newsfilter.search_items('sub')]
        self.assertTrue('art1' in resids)
        self.assertTrue('art2' not in resids)
        self.assertTrue('art3' in resids)
        self.assertEquals(2, len(resids))

    def test_display_datetime(self):
        self.newsfilter.set_subjects(['sub', 'sub2'])
        self.newsfilter.set_target_audiences(['ta', 'ta2'])
        self.newsfilter.set_sources([self.source1, self.source3])
        items = self.newsfilter.get_last_items(2)
        itemids = [item.id for item in items]
        """first test to see the order of the articles"""
        self.assertEquals(itemids, ['art1', 'art2'])
        """now change the display datetime of the second article
           to be ahead of the first article, the order
           should change"""
        self.item1_2.get_viewable().set_display_datetime(DateTime() + 1)
        items = self.newsfilter.get_last_items(2)
        itemids = [item.id for item in items]
        self.assertEquals(set(itemids), set(['art2', 'art1']))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsFilterTestCase))
    suite.addTest(unittest.makeSuite(SourcesNewsFilterTestCase))
    return suite
