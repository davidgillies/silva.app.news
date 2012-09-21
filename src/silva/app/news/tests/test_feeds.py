
import unittest
from datetime import datetime

from zope.component import queryMultiAdapter
from zope.interface.verify import verifyObject
from Products.Silva.testing import TestRequest

from silva.app.news.interfaces import INewsItem, IAgendaItem
from silva.app.news.datetimeutils import local_timezone
from silva.app.news.tests.SilvaNewsTestCase import SilvaNewsTestCase
from silva.core.interfaces import IFeedEntry

from dateutil.relativedelta import relativedelta


class TestFeeds(SilvaNewsTestCase):
    """ Test atom and rss feeds
    """

    def setUp(self):
        super(TestFeeds, self).setUp()
        # Publication
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('source', 'Publication')
        factory.manage_addNewsFilter('filter', 'Filter')
        factory.manage_addNewsViewer('viewer', 'Viewer')

        self.root.filter.set_show_agenda_items(True)
        self.root.filter.add_source(self.root.source)
        self.root.viewer.add_filter(self.root.filter)

        # Items
        self.add_published_news_item(
            self.root.source, 'raining', 'The rain is coming')
        self.add_published_news_item(
            self.root.source, 'cows', 'Cows are moving in town')
        start_event = datetime(2010, 10, 9, 8, 20, 00, tzinfo=local_timezone)
        end_event = start_event + relativedelta(hours=+2)
        self.add_published_agenda_item(
            self.root.source, 'war', 'This is War', start_event, end_event)

    def test_feeds_agenda_item(self):
        entry = queryMultiAdapter(
            (self.root.source.war, TestRequest()),
            IFeedEntry)
        self.assertTrue(verifyObject(IAgendaItem, self.root.source.war))
        self.assertTrue(verifyObject(IFeedEntry, entry))
        self.assertEqual(entry.id(), 'http://localhost/root/source/war')
        self.assertEqual(entry.title(), 'This is War')
        self.assertEqual(entry.url(), 'http://localhost/root/source/war')
        self.assertEqual(entry.authors(), ['manager'])
        self.assertEqual(entry.description(), '')
        self.assertEqual(entry.keywords(), [])
        self.assertEqual(entry.html_description(), "<p></p>")
        self.assertEqual(entry.location(), '')
        self.assertEqual(entry.start_datetime(), '2010-10-09T08:20:00+02:00')
        self.assertEqual(entry.end_datetime(), '2010-10-09T10:20:00+02:00')

    def test_feeds_news_item(self):
        entry = queryMultiAdapter(
            (self.root.source.cows, TestRequest()),
            IFeedEntry)
        self.assertTrue(verifyObject(INewsItem, self.root.source.cows))
        self.assertTrue(verifyObject(IFeedEntry, entry))
        self.assertEqual(entry.id(), 'http://localhost/root/source/cows')
        self.assertEqual(entry.title(), 'Cows are moving in town')
        self.assertEqual(entry.url(), 'http://localhost/root/source/cows')
        self.assertEqual(entry.authors(), ['manager'])
        self.assertEqual(entry.description(), '')
        self.assertEqual(entry.keywords(), [])
        self.assertEqual(entry.html_description(), "<p></p>")

    def test_functional_rss_feed_from_viewer(self):
        """Test that you can get a rss feeds from a news viewer.
        """
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('http://localhost/root/viewer/rss.xml'),
                200)
            self.assertEqual(
                browser.content_type,
                'text/xml;charset=UTF-8')

            items = browser.xml.xpath(
                '//rss:item', namespaces={'rss': "http://purl.org/rss/1.0/"})
            # We have two news items, and one agenda item.
            self.assertEquals(3, len(items))

    def test_functional_atom_feed_from_viewer(self):
        """Test that you can get an atom from a news viewer.
        """
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('http://localhost/root/viewer/atom.xml'),
                200)
            self.assertEqual(
                browser.content_type,
                'text/xml;charset=UTF-8')

            items = browser.xml.xpath(
                '//atom:entry', namespaces={'atom': "http://www.w3.org/2005/Atom"})
            # We have two news items, and one agenda item.
            self.assertEquals(3, len(items))

    def test_functional_rss_feed_from_publication(self):
        """Test that you can get a rss feeds from a default news publication.
        """
        with self.layer.get_browser() as browser:
            # Feeds are disabled by default (container settings)
            self.assertEqual(
                browser.open('http://localhost/root/source/rss.xml'),
                404)
            # If you enable them when they should work
            self.root.source.set_allow_feeds(True)
            self.assertEqual(
                browser.open('http://localhost/root/source/rss.xml'),
                200)
            self.assertEqual(
                browser.content_type,
                'text/xml;charset=UTF-8')

            items = browser.xml.xpath(
                '//rss:item', namespaces={'rss': "http://purl.org/rss/1.0/"})
            # We only have two items, since the feed is only enabled
            # for news and not agenda items
            self.assertEquals(2, len(items))

    def test_functional_atom_feed_from_publication(self):
        """Test that you can get an atom from a default news publication.
        """
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('http://localhost/root/source/atom.xml'),
                404)
            # If you enable them when they should work
            self.root.source.set_allow_feeds(True)
            self.assertEqual(
                browser.open('http://localhost/root/source/atom.xml'),
                200)
            self.assertEqual(
                browser.content_type,
                'text/xml;charset=UTF-8')

            items = browser.xml.xpath(
                '//atom:entry', namespaces={'atom': "http://www.w3.org/2005/Atom"})
            # We only have two items, since the feed is only enabled
            # for news and not agenda items
            self.assertEquals(2, len(items))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFeeds))
    return suite
