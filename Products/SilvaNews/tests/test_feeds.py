from Products.SilvaNews.datetimeutils import local_timezone
from Products.SilvaNews.tests.SilvaNewsTestCase import SilvaNewsTestCase
from dateutil.relativedelta import relativedelta
from datetime import datetime
from lxml import etree


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
        status = browser.open('http://localhost/root/viewer/rss.xml')
        self.assertEquals(200, status)
        xml = etree.fromstring(browser.contents)
        ns = { 'rss': "http://purl.org/rss/1.0/"}
        items = xml.xpath('//rss:item', namespaces=ns)
        self.assertEquals(3, len(items))

    def test_atom_feed(self):
        browser = self.layer.get_browser()
        browser.options.handle_errors = False
        status = browser.open('http://localhost/root/viewer/atom.xml')
        self.assertEquals(200, status)
        xml = etree.fromstring(browser.contents)
        ns = { 'atom': "http://www.w3.org/2005/Atom"}
        items = xml.xpath('//atom:entry', namespaces=ns)
        self.assertEquals(3, len(items))


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFeeds))
    return suite
