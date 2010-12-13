import unittest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from Products.SilvaNews.tests.SilvaNewsTestCase import (NewsBaseTestCase,
    SilvaNewsTestCase)
from Products.SilvaNews.datetimeutils import local_timezone
from lxml.cssselect import CSSSelector


def register_inspect(browser):
    browser.inspect.add('news_items',
        CSSSelector('div.newsitemlistitem').path)


class TestViewerPublicViews(NewsBaseTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.browser = self.layer.get_browser()
        self.browser.options.handle_errors = False
        register_inspect(self.browser)

    def test_index(self):
        status = self.browser.open('http://localhost/root/newsviewer')
        self.assertEquals(200, status)
        self.assertEquals(len(self.browser.inspect.news_items), 2)

    def test_archive(self):
        status = self.browser.open('http://localhost/root/newsviewer/archives')
        self.assertEquals(200, status)
        self.assertEquals(len(self.browser.inspect.news_items), 2)


class TestAgendaViewerPublicViews(SilvaNewsTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.browser = self.layer.get_browser()
        self.root = self.layer.get_application()
        self.browser.options.handle_errors = False
        register_inspect(self.browser)

        news_publication = self.add_news_publication(
            self.root, 'news_publication', 'News Publication')
        agenda_filter = self.add_agenda_filter(
            self.root, 'agenda_filter', 'Agenda Filter')
        agenda_viewer = self.add_agenda_viewer(
            self.root, 'agenda_viewer', 'AgendaViewer')

        agenda_filter.set_target_audiences(['ta'])
        agenda_filter.set_subjects(['sub'])
        agenda_filter.add_source(news_publication)
        agenda_viewer.add_filter(agenda_filter)

        sdt = datetime(2010, 12, 10, 8, 20, tzinfo=local_timezone)

        self.add_published_agenda_item(
            news_publication, 'event0', 'Some Event',
            sdt, sdt + relativedelta(hours=+3))

        self.add_published_agenda_item(
            news_publication, 'event1', 'Some Other Event',
            sdt, sdt + relativedelta(days=+3), all_day=True)

    def test_index(self):
        status = self.browser.open('http://localhost/root/agenda_viewer',
            query={'year': '2010', 'month': '12', 'day': '10'})
        self.assertEquals(200, status)
        self.assertEquals(len(self.browser.inspect.news_items), 2)

    def test_archives(self):
        status = self.browser.open(
            'http://localhost/root/agenda_viewer/archives',
            query={'year': '2010', 'month': '12'})
        self.assertEquals(200, status)
        self.assertEquals(len(self.browser.inspect.news_items), 2)

    def test_year(self):
        status = self.browser.open(
            'http://localhost/root/agenda_viewer/year', query={'year': '2010'})

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestViewerPublicViews))
    suite.addTest(unittest.makeSuite(TestAgendaViewerPublicViews))
    return suite

