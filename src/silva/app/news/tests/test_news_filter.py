# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from DateTime import DateTime

from zope.interface.verify import verifyObject

from silva.core.services.interfaces import ICataloging
from silva.core.interfaces import IPublicationWorkflow
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
        factory.manage_addNewsFilter('filter', 'News Filter')
        nfilter = self.root._getOb('filter', None)
        self.assertTrue(verifyObject(INewsFilter, nfilter))


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
        factory.manage_addNewsFilter('filter', 'Filter')

        now = DateTime()
        factory = self.root.news.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('snowing', 'It is snowing')
        factory.manage_addNewsItem('rain', 'It rained')
        factory.manage_addAgendaItem('sun', 'Sun hours')
        IPublicationWorkflow(self.root.news.rain).approve(now - 10)
        IPublicationWorkflow(self.root.news.rain).new_version()
        IPublicationWorkflow(self.root.news.snowing).approve(now - 5)
        IPublicationWorkflow(self.root.news.snowing).new_version()
        IPublicationWorkflow(self.root.news.sun).publish()
        IPublicationWorkflow(self.root.news.sun).new_version()

        factory = self.root.events.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('release', 'Release Article')
        factory.manage_addAgendaItem('party', 'Release Party')

    def test_sources(self):
        """Test get_sources, set_sources and has_sources.
        """
        self.assertFalse(self.root.filter.has_sources())
        self.assertItemsEqual(
            self.root.filter.get_sources(),
            [])

        self.root.filter.set_sources([self.root.news, self.root.events])
        self.assertTrue(self.root.filter.has_sources())
        self.assertItemsEqual(
            self.root.filter.get_sources(),
            [self.root.news, self.root.events])

        self.root.manage_delObjects(['events'])
        self.assertTrue(self.root.filter.has_sources())
        self.assertItemsEqual(
            self.root.filter.get_sources(),
            [self.root.news])

    def test_excluded_items(self):
        """Test methods to manage excluded items.
        """
        self.assertItemsEqual(
            self.root.filter.get_excluded_items(),
            [])

        excluded = self.root.news.rain
        self.assertFalse(self.root.filter.is_excluded_item(excluded))

        # Add the element to the list of excluded items.
        self.root.filter.add_excluded_item(excluded)
        self.assertTrue(self.root.filter.is_excluded_item(excluded))
        self.assertItemsEqual(
            self.root.filter.get_excluded_items(),
            [excluded])

        # Remove the element from the list of excluded items
        self.root.filter.remove_excluded_item(excluded)
        self.assertFalse(self.root.filter.is_excluded_item(excluded))
        self.assertItemsEqual(
            self.root.filter.get_excluded_items(),
            [])

    def test_get_items(self):
        """Get get_items family methods.
        """
        self.root.filter.set_sources([self.root.news])

        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_all_items()],
            ['/root/news/snowing/0', '/root/news/snowing/1',
             '/root/news/rain/0', '/root/news/rain/1'])
        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_next_items(10)],
           [])
        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_last_items(10)],
            ['/root/news/snowing/0', '/root/news/rain/0'])

    def test_get_items_excluded(self):
        """Test that get_items family methods don't return excluded items.
        """
        self.root.filter.set_sources([self.root.news])
        self.root.filter.add_excluded_item(self.root.news.rain)

        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_all_items()],
            ['/root/news/snowing/0', '/root/news/snowing/1',
             '/root/news/rain/0', '/root/news/rain/1'])
        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_next_items(10)],
           [])
        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_last_items(10)],
            ['/root/news/snowing/0'])

    def test_get_items_with_agenda(self):
        """Test get_items family methods with agenda items.
        """
        self.root.filter.set_sources([self.root.news])
        self.assertFalse(self.root.filter.show_agenda_items())
        self.root.filter.set_show_agenda_items(True)
        self.assertTrue(self.root.filter.show_agenda_items())

        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_all_items()],
            ['/root/news/snowing/0', '/root/news/snowing/1',
             '/root/news/rain/0', '/root/news/rain/1',
             '/root/news/sun/0', '/root/news/sun/1'])
        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_next_items(10)],
           ['/root/news/snowing/0', '/root/news/rain/0'])
        self.assertItemsEqual(
           [b.getPath() for b in self.root.filter.get_last_items(10)],
            ['/root/news/snowing/0', '/root/news/rain/0', '/root/news/sun/0'])

    def test_search_items(self):
        """Search items.
        """
        self.root.filter.set_sources([self.root.news])

        self.assertItemsEqual(
            map(lambda b: b.getPath(), self.root.filter.search_items('It')),
            ['/root/news/snowing/0', '/root/news/rain/0'])
        self.assertItemsEqual(
            map(lambda b: b.getPath(), self.root.filter.search_items('sun')),
            [])

    def test_search_items_excluded(self):
        """Search items. An excluded items is not returned.
        """
        self.root.filter.set_sources([self.root.news])
        self.root.filter.add_excluded_item(self.root.news.rain)

        self.assertItemsEqual(
            map(lambda b: b.getPath(), self.root.filter.search_items('It')),
            ['/root/news/snowing/0',])
        self.assertItemsEqual(
            map(lambda b: b.getPath(), self.root.filter.search_items('rained')),
            [])

    def test_search_items_with_agenda(self):
        """Search items, including agenda items.
        """
        self.root.filter.set_sources([self.root.news])
        self.root.filter.set_show_agenda_items(True)
        self.assertTrue(self.root.filter.show_agenda_items())

        self.assertItemsEqual(
            map(lambda b: b.getPath(), self.root.filter.search_items('It')),
            ['/root/news/snowing/0', '/root/news/rain/0'])
        self.assertItemsEqual(
            map(lambda b: b.getPath(), self.root.filter.search_items('sun')),
            ['/root/news/sun/0'])

    def test_display_datetime(self):
        """Verify that the items should be sorted on their display
        datetime.
        """
        self.root.filter.set_sources([self.root.news])
        rain = self.root.news.rain.get_viewable()
        snowing = self.root.news.snowing.get_viewable()

        # We can change the display_datetime.
        rain.set_display_datetime(DateTime() + 10)
        snowing.set_display_datetime(DateTime() - 10)
        self.assertGreater(
            rain.get_display_datetime(),
            snowing.get_display_datetime())

        # Snowing should be after rain.
        self.assertEqual(
           [b.getPath() for b in self.root.filter.get_last_items(10)],
            ['/root/news/rain/0', '/root/news/snowing/0'])

        rain.set_display_datetime(DateTime() - 10)
        snowing.set_display_datetime(DateTime() + 10)
        self.assertGreater(
            snowing.get_display_datetime(),
            rain.get_display_datetime())

        # Reindex the changes.
        ICataloging(rain).reindex()
        ICataloging(snowing).reindex()

        # This should invert the sort order.
        self.assertEqual(
           [b.getPath() for b in self.root.filter.get_last_items(10)],
            ['/root/news/snowing/0', '/root/news/rain/0'])



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsFilterTestCase))
    suite.addTest(unittest.makeSuite(SourcesNewsFilterTestCase))
    return suite
