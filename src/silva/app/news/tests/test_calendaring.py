# coding=utf-8

from datetime import datetime, timedelta
import unittest

from dateutil.relativedelta import relativedelta

from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from silva.core.services.interfaces import ICatalogingAttributes
from silva.app.news.tests.SilvaNewsTestCase import (SilvaNewsTestCase,
    NewsBaseTestCase)
from silva.app.news.datetimeutils import (local_timezone,
    datetime_to_unixtimestamp, get_timezone)


class CalendaringTestCase(SilvaNewsTestCase):

    def test_event_indexing(self):
        start = datetime.now(local_timezone)
        self.add_published_agenda_item(
            self.root, 'weekend', 'Agenda Item', start, start + timedelta(60))

        version = self.root.weekend.get_viewable()
        # make sure it does not raise
        self.assertNotEquals(
            ICatalogingAttributes(version).timestamp_ranges(),
            [])

        start_index = datetime_to_unixtimestamp(start)
        end_index = datetime_to_unixtimestamp(start + timedelta(30))
        brains = self.root.service_catalog(
            {'timestamp_ranges': {'query': [start_index, end_index]}})
        self.assertEqual(
            [brain.getObject() for brain in brains],
            [version])

        start_index = datetime_to_unixtimestamp(start - timedelta(30))
        end_index = datetime_to_unixtimestamp(start - timedelta(20))
        brains = self.root.service_catalog(
            {'timestamp_ranges': {'query': [start_index, end_index]}})
        self.assertEqual(
            [brain.getObject() for brain in brains],
            [])



class TestAgendaViewerLookup(NewsBaseTestCase):

    def setUp(self):
        super(TestAgendaViewerLookup, self).setUp()
        self.tz = get_timezone('Europe/Amsterdam')
        root = self.layer.get_application()
        factory = root.manage_addProduct['silva.app.news']
        factory.manage_addAgendaFilter('agenda_filter', 'Agenda Filter')
        factory.manage_addAgendaViewer('agenda_viewer', 'Agenda Viewer')
        self.root.agenda_viewer.set_timezone_name('Europe/Amsterdam')
        factory.manage_addNewsPublication(
            'news_publication', 'News Publication')

        self.root.agenda_filter.set_sources([self.root.news_publication])
        self.root.agenda_filter.set_subjects(['sub'])
        self.root.agenda_filter.set_target_audiences(['ta'])

        self.root.agenda_viewer.set_filters([self.root.agenda_filter])

        self.news_pub_factory = \
            self.root.news_publication.manage_addProduct['SilvaNews']

    def test_month_lookup(self):
        self.add_published_agenda_item(
            self.root.news_publication,
            'start_before_month',
            'This agenda item starts before the month and ends at the'
            'beginning of the month',
            datetime(2010, 10, 23, 12, 20, tzinfo=self.tz),
            datetime(2010, 11, 2, 12, 00, tzinfo=self.tz))

        self.add_published_agenda_item(
            self.root.news_publication,
            'end_after_month',
            'This agenda item ends before after the month ends',
            datetime(2010, 11, 23, 12, 20, tzinfo=self.tz),
            datetime(2010, 12, 2, 12, 00, tzinfo=self.tz))

        self.add_published_agenda_item(
            self.root.news_publication,
            'out_of_range',
            'This agenda item is not found it is out of range',
            datetime(2010, 10, 23, 12, 20, tzinfo=self.tz),
            datetime(2010, 10, 30, 12, 00, tzinfo=self.tz))

        self.add_published_agenda_item(
            self.root.news_publication,
            'over_month',
            'This agenda item starts before month starts'
            'and ends after month ends',
            datetime(2010, 10, 23, 12, 20, tzinfo=self.tz),
            datetime(2010, 12, 3, 02, 00, tzinfo=self.tz))

        self.add_published_agenda_item(
            self.root.news_publication,
            'within_month',
            'This agenda item starts after month starts'
            'and ends before month ends',
            datetime(2010, 11, 23, 12, 20, tzinfo=self.tz),
            datetime(2010, 11, 23, 22, 00, tzinfo=self.tz))

        versions = set([
            self.root.news_publication.start_before_month.get_viewable(),
            self.root.news_publication.end_after_month.get_viewable(),
            self.root.news_publication.over_month.get_viewable(),
            self.root.news_publication.within_month.get_viewable(),
            ])

        agenda = self.root.agenda_viewer

        def normalize(results):
            return set(map(lambda x: x.getObject(), items))

        items = agenda.get_items_by_date(11, 2010)
        self.assertEquals(versions, normalize(items))

        items = agenda.get_items_by_date_range(
            datetime(2010, 11, 1, 00, 00, tzinfo=self.tz),
            datetime(2010, 11, 30, 23, 59, 59, tzinfo=self.tz))
        self.assertEquals(versions, normalize(items))


def get_identifier(content):
    return getUtility(IIntIds).getId(content)


class TestCalendar(NewsBaseTestCase):

    def setUp(self):
        super(TestCalendar, self).setUp()
        # Publication
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('source', 'Publication')
        # Filter
        factory.manage_addAgendaFilter('filter', 'Agenda Filter')
        self.root.filter.set_subjects(['sub'])
        self.root.filter.set_target_audiences(['ta'])
        self.root.filter.set_sources([self.root.source])
        # Viewer
        factory.manage_addAgendaViewer('agenda', 'Agenda')
        self.root.agenda.add_filter(self.root.filter)
        self.root.agenda.set_timezone_name('Europe/Amsterdam')

        timezone = self.root.agenda.get_timezone()
        sdt = datetime(2012, 6, 4, 10, 20, tzinfo=timezone)
        self.add_published_agenda_item(
            self.root.source, 'saturday', u'Saturday “π” aka Disco',
            sdt, sdt + relativedelta(hours=+1))

        sdt = datetime(2012, 6, 10, 10, 20, tzinfo=timezone)
        self.event2 = self.add_published_agenda_item(
            self.root.source, 'sunday', u'Sunday pépère héhé!',
            sdt, sdt + relativedelta(days=+1), all_day=True)

    def test_functional_calendar_view(self):
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('http://localhost/root/agenda'),
                200)

    def test_functional_calendar_view_for_event(self):
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open(
                    'http://localhost/root/agenda',
                    query={'year': '2012', 'month': '6', 'day': '4'}),
                200)

            nodes = browser.html.xpath(
                '//div[@id="event_%s"]' % get_identifier(
                    self.root.source.saturday.get_viewable()))
            self.assertTrue(len(nodes), 1)

    def test_functional_external_source_view(self):
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('http://localhost/root/agenda/external_source'),
                200)

    def test_functional_subscribe_view(self):
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('http://localhost/root/agenda/subscribe.html'),
                200)

    def test_functional_ics_view(self):
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('http://localhost/root/agenda/calendar.ics'),
                200)
            uids = (get_identifier(self.root.source.sunday.get_viewable()),
                    get_identifier(self.root.source.saturday.get_viewable()))
            self.assertEqual(
                browser.contents.replace("\r\n", "\n"),
                """BEGIN:VCALENDAR
PRODID:-//Infrae SilvaNews Calendaring//NONSGML Calendar//EN
VERSION:2.0
X-WR-CALNAME:Agenda
X-WR-TIMEZONE:Europe/Amsterdam
BEGIN:VEVENT
DTEND;VALUE=DATE:20120612
DTSTART;VALUE=DATE:20120610
SUMMARY:Event2
UID:%d@0@silvanews
URL:http://localhost/root/source1/event2
END:VEVENT
BEGIN:VEVENT
DTEND:20120604T092000Z
DTSTART:20120604T082000Z
SUMMARY:Event héhé“π”
UID:%d@0@silvanews
URL:http://localhost/root/source1/event1
END:VEVENT
END:VCALENDAR
""" % uids)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CalendaringTestCase))
    suite.addTest(unittest.makeSuite(TestCalendar))
    suite.addTest(unittest.makeSuite(TestAgendaViewerLookup))
    return suite
