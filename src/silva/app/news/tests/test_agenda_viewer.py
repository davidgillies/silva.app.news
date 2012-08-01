# coding=utf-8

from datetime import datetime, timedelta
import unittest

from dateutil.relativedelta import relativedelta

from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.ftesting import public_settings
from Products.Silva.testing import assertTriggersEvents

from silva.core.services.interfaces import ICatalogService
from silva.core.services.interfaces import ICatalogingAttributes
from silva.app.news.interfaces import IAgendaViewer
from silva.app.news.tests.SilvaNewsTestCase import SilvaNewsTestCase
from silva.app.news.testing import get_identifier
from silva.app.news.datetimeutils import (local_timezone,
    datetime_to_unixtimestamp, get_timezone)


def calendar_settings(browser):
    public_settings(browser)
    browser.inspect.add(
        'newsitems',
        css=".newsitemheading",
        type='text')


class AgendaViewerTestCase(SilvaNewsTestCase):

    def test_viewer(self):
        factory = self.root.manage_addProduct['silva.app.news']
        with assertTriggersEvents('ContentCreatedEvent'):
            factory.manage_addAgendaViewer('viewer', 'Agenda Viewer')
        viewer = self.root._getOb('viewer', None)
        self.assertTrue(verifyObject(IAgendaViewer, viewer))

    def test_catalog(self):
        start = datetime.now(local_timezone)
        self.add_published_agenda_item(
            self.root, 'weekend', 'Agenda Item', start, start + timedelta(60))

        # make sure it does not raise
        self.assertNotEqual(
            ICatalogingAttributes(self.root.weekend.get_viewable()).timestamp_ranges(),
            [])

        start_index = datetime_to_unixtimestamp(start)
        end_index = datetime_to_unixtimestamp(start + timedelta(30))
        catalog = getUtility(ICatalogService)
        brains = catalog(
            {'timestamp_ranges': {'query': [start_index, end_index]}})
        self.assertEqual(
            [b.getPath() for b in brains],
            ['/root/weekend/0'])

        start_index = datetime_to_unixtimestamp(start - timedelta(30))
        end_index = datetime_to_unixtimestamp(start - timedelta(20))
        brains = catalog(
            {'timestamp_ranges': {'query': [start_index, end_index]}})
        self.assertEqual(
            [b.getPath() for b in brains],
            [])

    def test_get_item_by_date(self):
        """Test the various methods that get_items by date.
        """
        timezone = get_timezone('Europe/Amsterdam')
        root = self.layer.get_application()
        factory = root.manage_addProduct['silva.app.news']
        factory.manage_addAgendaFilter('filter', 'Agenda Filter')
        factory.manage_addAgendaViewer('viewer', 'Agenda Viewer')
        factory.manage_addNewsPublication('news', 'News Publication')

        self.root.filter.set_sources([self.root.news])
        self.root.viewer.set_filters([self.root.filter])
        self.root.viewer.set_timezone_name('Europe/Amsterdam')

        self.add_published_agenda_item(
            self.root.news,
            'start_before_month',
            'This agenda item starts before the month and ends at the'
            'beginning of the month',
            datetime(2010, 10, 23, 12, 20, tzinfo=timezone),
            datetime(2010, 11, 2, 12, 00, tzinfo=timezone))

        self.add_published_agenda_item(
            self.root.news,
            'end_after_month',
            'This agenda item ends before after the month ends',
            datetime(2010, 11, 23, 12, 20, tzinfo=timezone),
            datetime(2010, 12, 2, 12, 00, tzinfo=timezone))

        self.add_published_agenda_item(
            self.root.news,
            'out_of_range',
            'This agenda item is not found it is out of range',
            datetime(2010, 10, 23, 12, 20, tzinfo=timezone),
            datetime(2010, 10, 30, 12, 00, tzinfo=timezone))

        self.add_published_agenda_item(
            self.root.news,
            'over_month',
            'This agenda item starts before month starts'
            'and ends after month ends',
            datetime(2010, 10, 23, 12, 20, tzinfo=timezone),
            datetime(2010, 12, 3, 02, 00, tzinfo=timezone))

        self.add_published_agenda_item(
            self.root.news,
            'within_month',
            'This agenda item starts after month starts'
            'and ends before month ends',
            datetime(2010, 11, 23, 12, 20, tzinfo=timezone),
            datetime(2010, 11, 23, 22, 00, tzinfo=timezone))

        self.assertEquals(
            [b.getPath() for b in self.root.viewer.get_items_by_date(11, 2010)],
            ['/root/news/end_after_month/0',
             '/root/news/within_month/0',
             '/root/news/start_before_month/0',
             '/root/news/over_month/0'])
        self.assertEquals(
            [b.getPath() for b in self.root.viewer.get_items_by_date_range(
                    datetime(2010, 11, 1, 00, 00, tzinfo=timezone),
                    datetime(2010, 11, 30, 23, 59, 59, tzinfo=timezone)
                    )],
            ['/root/news/end_after_month/0',
             '/root/news/within_month/0',
             '/root/news/start_before_month/0',
             '/root/news/over_month/0'])


def format_date(date):
    return date.utcdatetime().strftime('%Y%m%dT%H%M%SZ')


class RenderAgendaViewerTestCase(SilvaNewsTestCase):
    maxDiff = None

    def setUp(self):
        super(RenderAgendaViewerTestCase, self).setUp()
        # Publication
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('source', 'Publication')
        factory.manage_addAgendaFilter('filter', 'Agenda Filter')
        factory.manage_addAgendaViewer('agenda', 'Agenda')

        self.root.filter.set_sources([self.root.source])
        self.root.agenda.add_filter(self.root.filter)
        self.root.agenda.set_timezone_name('Europe/Amsterdam')

        timezone = self.root.agenda.get_timezone()
        sdt = datetime(2012, 6, 4, 10, 20, tzinfo=timezone)
        self.add_published_agenda_item(
            self.root.source, 'saturday', u'Saturday “π” aka Disco',
            sdt, sdt + relativedelta(hours=+1))

        sdt = datetime(2012, 6, 10, 10, 20, tzinfo=timezone)
        self.add_published_agenda_item(
            self.root.source, 'sunday', u'Sunday pépère héhé!',
            sdt, sdt + relativedelta(days=+1), all_day=True)

    def test_rendering(self):
        with self.layer.get_browser(calendar_settings) as browser:
            self.assertEqual(browser.open('/root/agenda'), 200)
            self.assertIn('Agenda', browser.inspect.title)
            self.assertEqual(browser.inspect.newsitems, [])

    def test_rendering_with_event(self):
        with self.layer.get_browser(calendar_settings) as browser:
            self.assertEqual(
                browser.open(
                    '/root/agenda',
                    query={'year': '2012', 'month': '6', 'day': '4'}),
                200)
            self.assertIn('Agenda', browser.inspect.title)
            self.assertEqual(
                browser.inspect.newsitems,
                [u'Saturday “π” aka Disco'])

    def test_functional_external_source_view(self):
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('http://localhost/root/agenda/external_source'),
                200)

    def test_year(self):
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('/root/agenda/year.html'),
                200)

    def test_archive(self):
        with self.layer.get_browser(calendar_settings) as browser:
            self.assertEqual(
                browser.open('/root/agenda/archives.html'),
                200)

    def test_calendar(self):
        with self.layer.get_browser(calendar_settings) as browser:
            self.assertEqual(
                browser.open('/root/agenda/calendar.html'),
                200)
            self.assertIn('Agenda', browser.inspect.title)

    def test_subscribe(self):
        with self.layer.get_browser(calendar_settings) as browser:
            self.assertEqual(
                browser.open('/root/agenda/subscribe.html'),
                200)
            self.assertIn('Agenda', browser.inspect.title)

    def test_ics(self):
        events = self.root.source
        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/agenda/calendar.ics'), 200)
            self.assertEqual(
                browser.content_type,
                'text/calendar;charset=utf-8')
            self.assertMultiLineEqual(
                browser.contents.replace("\r\n", "\n"),
                u"""BEGIN:VCALENDAR
PRODID:-//Infrae SilvaNews Calendaring//NONSGML Calendar//EN
VERSION:2.0
X-WR-CALNAME:Agenda
X-WR-TIMEZONE:Europe/Amsterdam
BEGIN:VEVENT
CREATED:%(sunday_created)s
DTEND;VALUE=DATE:20120612
DTSTART;VALUE=DATE:20120610
LAST-MODIFIED:%(sunday_modified)s
SUMMARY:Sunday pépère héhé!
UID:%(sunday_id)s@0@silvanews
URL:http://localhost/root/source/sunday
END:VEVENT
BEGIN:VEVENT
CREATED:%(saturday_created)s
DTEND:20120604T092000Z
DTSTART:20120604T082000Z
LAST-MODIFIED:%(saturday_modified)s
SUMMARY:Saturday “π” aka Disco
UID:%(saturday_id)s@0@silvanews
URL:http://localhost/root/source/saturday
END:VEVENT
END:VCALENDAR
""" % {'sunday_id': get_identifier(events.sunday.get_viewable()),
       'sunday_created': format_date(events.sunday.get_creation_datetime()),
       'sunday_modified': format_date(events.sunday.get_modification_datetime()),
       'saturday_id': get_identifier(events.saturday.get_viewable()),
       'saturday_created': format_date(events.saturday.get_creation_datetime()),
       'saturday_modified': format_date(events.saturday.get_modification_datetime())
       })


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AgendaViewerTestCase))
    suite.addTest(unittest.makeSuite(RenderAgendaViewerTestCase))
    return suite
