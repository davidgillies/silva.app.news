
import unittest

from silva.app.news.datetimeutils import local_timezone
from silva.app.news.tests.SilvaNewsTestCase import SilvaNewsTestCase
from dateutil.relativedelta import relativedelta
from datetime import datetime


class TestFeeds(SilvaNewsTestCase):
    """ Test atom and rss feeds
    """

    def setUp(self):
        super(TestFeeds, self).setUp()
        self.news_publication = self.add_news_publication(
            self.root, 'publication', 'Publication')
        self.news_filter = self.add_news_filter(
            self.root, 'filter', 'Filter')
        self.news_filter.set_target_audiences(['ta'])
        self.news_filter.set_subjects(['sub'])
        self.news_viewer = self.add_news_viewer(
            self.root, 'viewer', 'Viewer')
        self.news_filter.set_show_agenda_items(True)
        self.news_filter.add_source(self.news_publication)
        self.news_viewer.add_filter(self.news_filter)

        self.add_published_news_item(self.news_publication, 'item1', 'Item')
        self.add_published_news_item(self.news_publication, 'item2', 'Item 2')
        sdt = datetime(2010, 10, 9, 8, 20, 00, tzinfo=local_timezone)
        edt = sdt + relativedelta(hours=+2)
        self.add_published_agenda_item(
            self.news_publication, 'event1', 'Event1', sdt, edt)

    def test_rss_feed(self):
        browser = self.layer.get_browser()
        browser.options.handle_errors = False
        self.assertEqual(
            browser.open('http://localhost/root/viewer/rss.xml'),
            200)
        self.assertEqual(
            browser.content_type, 'text/xml;charset=UTF-8')

        ns = { 'rss': "http://purl.org/rss/1.0/"}
        items = browser.xml.xpath('//rss:item', namespaces=ns)
        self.assertEquals(3, len(items))

    def test_atom_feed(self):
        browser = self.layer.get_browser()
        browser.options.handle_errors = False
        self.assertEqual(
            browser.open('http://localhost/root/viewer/rss.xml'),
            200)
        self.assertEqual(
            browser.content_type, 'text/xml;charset=UTF-8')

        ns = { 'atom': "http://www.w3.org/2005/Atom"}
        items = browser.xml.xpath('//atom:entry', namespaces=ns)
        self.assertEquals(3, len(items))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFeeds))
    return suite
