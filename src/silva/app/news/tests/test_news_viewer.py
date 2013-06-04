# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.interface.verify import verifyObject

from Products.Silva.ftesting import public_settings
from Products.Silva.testing import tests

from silva.app.news.interfaces import INewsViewer
from silva.app.news.testing import FunctionalLayer
from silva.core.interfaces import IPublicationWorkflow


def news_settings(browser):
    public_settings(browser)
    browser.inspect.add(
        'newsitems',
        css=".newsitemheading",
        type='text')


class NewsViewerTestCase(unittest.TestCase):
    """Test the NewsViewer interface.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_viewer(self):
        factory = self.root.manage_addProduct['silva.app.news']
        with tests.assertTriggersEvents('ContentCreatedEvent'):
            factory.manage_addNewsViewer('viewer', 'News Viewer')
        viewer = self.root._getOb('viewer', None)
        self.assertTrue(verifyObject(INewsViewer, viewer))


class FilterNewsViewerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News')
        factory.manage_addNewsFilter('private', 'Private Filterx')
        factory.manage_addNewsFilter('public', 'Public Filter')
        factory.manage_addNewsViewer('viewer', 'News Viewer')
        factory = self.root.news.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('snowing', 'It is snowing')
        factory.manage_addNewsItem('rain', 'It rained')
        IPublicationWorkflow(self.root.news.rain).publish()
        IPublicationWorkflow(self.root.news.rain).new_version()
        IPublicationWorkflow(self.root.news.snowing).publish()
        IPublicationWorkflow(self.root.news.snowing).new_version()

        self.root.private.set_sources([self.root.news])
        self.root.viewer.add_filter(self.root.private)

    def test_filters(self):
        """Test methods to manage filters.
        """
        self.assertTrue(self.root.viewer.has_filter())
        tests.assertContentItemsEqual(
            self.root.viewer.get_filters(),
            [self.root.private])
        self.root.viewer.add_filter(self.root.public)
        tests.assertContentItemsEqual(
            self.root.viewer.get_filters(),
            [self.root.public, self.root.private])
        self.root.manage_delObjects(['private'])
        self.assertTrue(self.root.viewer.has_filter())
        tests.assertContentItemsEqual(
            self.root.viewer.get_filters(),
            [self.root.public])
        self.root.viewer.set_filters([])
        tests.assertContentItemsEqual(
            self.root.viewer.get_filters(),
            [])
        self.assertFalse(self.root.viewer.has_filter())

    def test_get_items(self):
        """Test that get_items family methods works.
        """
        self.assertItemsEqual(
            [b.getPath() for b in self.root.viewer.get_items()],
            ['/root/news/snowing/0', '/root/news/rain/0'])

        # Try to configure two filters
        self.root.viewer.add_filter(self.root.public)
        self.assertItemsEqual(
            [b.getPath() for b in self.root.viewer.get_items()],
            ['/root/news/snowing/0', '/root/news/rain/0'])

    def test_get_items_excluded(self):
        """Test that get_items family methods works when an item is
        ignored.
        """
        self.root.private.add_excluded_item(self.root.news.rain)

        self.assertItemsEqual(
            [b.getPath() for b in self.root.viewer.get_items()],
            ['/root/news/snowing/0'],)

    def test_search_items(self):
        """Search items must return items that contains the given words.
        """
        self.assertItemsEqual(
            [b.getPath() for b in self.root.viewer.search_items('rained')],
            ['/root/news/rain/0'])
        self.assertItemsEqual(
            [b.getPath() for b in self.root.viewer.search_items('sun')],
            [])

    def test_search_items_excluded(self):
        """Search items must ignore excluded items
        """
        self.root.private.add_excluded_item(self.root.news.rain)

        self.assertItemsEqual(
            [b.getPath() for b in self.root.viewer.search_items('rained')],
            [])
        self.assertItemsEqual(
            [b.getPath() for b in self.root.viewer.search_items('It')],
            ['/root/news/snowing/0'])


class RenderNewsViewerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News')
        factory.manage_addNewsFilter('filter', 'News Filter')
        factory.manage_addNewsViewer('viewer', 'News Viewer')
        factory = self.root.news.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('snowing', 'It is snowing')
        factory.manage_addNewsItem('rain', 'It rained')
        IPublicationWorkflow(self.root.news.rain).publish()
        IPublicationWorkflow(self.root.news.rain).new_version()
        IPublicationWorkflow(self.root.news.snowing).publish()
        IPublicationWorkflow(self.root.news.snowing).new_version()

        self.root.filter.set_sources([self.root.news])
        self.root.viewer.add_filter(self.root.filter)

    def test_rendering(self):
        with self.layer.get_browser(news_settings) as browser:
            self.assertEqual(browser.open('/root/viewer'), 200)
            self.assertEqual(browser.inspect.title, ['News Viewer'])
            self.assertItemsEqual(
                browser.inspect.newsitems,
                ['It is snowing', 'It rained'])

    def test_archive(self):
        with self.layer.get_browser(news_settings) as browser:
            self.assertEqual(
                browser.open('/root/viewer/archives.html'),
                200)
            self.assertItemsEqual(
                browser.inspect.newsitems,
                ['It is snowing', 'It rained'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsViewerTestCase))
    suite.addTest(unittest.makeSuite(FilterNewsViewerTestCase))
    suite.addTest(unittest.makeSuite(RenderNewsViewerTestCase))
    return suite
