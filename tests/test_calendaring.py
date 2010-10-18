from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from Products.SilvaNews.tests.SilvaNewsTestCase import (SilvaNewsTestCase,
    NewsBaseTestCase)
from Products.SilvaNews.datetimeutils import (local_timezone,
    datetime_to_unixtimestamp)


class TestEvent(SilvaNewsTestCase):

    def afterSetUp(self):
        super(TestEvent, self).afterSetUp()

    def test_event_indexing(self):
        start = datetime.now(local_timezone)
        self.add_published_agenda_item(self.root, 'ai1',
            'Agenda Item', start, start + timedelta(60))

        version = getattr(self.root.ai1, '0')
        # make sure it does not raise
        version.idx_timestamp_ranges()

        start_index = datetime_to_unixtimestamp(start)
        end_index = datetime_to_unixtimestamp(start + timedelta(30))
        brains = self.root.service_catalog(
            {'idx_timestamp_ranges': {'query': [start_index, end_index]}})
        l = [brain.getObject() for brain in brains]
        self.assertEqual(l, [version])

        start_index = datetime_to_unixtimestamp(start - timedelta(30))
        end_index = datetime_to_unixtimestamp(start - timedelta(20))
        brains = self.root.service_catalog(
            {'idx_timestamp_ranges': {'query': [start_index, end_index]}})
        self.assertFalse(brains)


class TestCalendar(NewsBaseTestCase):

    def setUp(self):
        super(TestCalendar, self).setUp()
        self.browser = self.layer.get_browser()
        self.browser.options.handle_errors = False
        self.filter = self.add_agenda_filter(
            self.root, 'afilter', 'Agenda Filter')
        self.filter.set_subjects(['sub'])
        self.filter.set_target_audiences(['ta'])
        self.filter.add_source('/root/source1', 1)
        self.agenda = self.add_agenda_viewer(self.root, 'agenda', 'Agenda')
        self.agenda.set_filters(['/root/afilter'])
        self.agenda.set_timezone_name('Europe/Amsterdam')
        sdt = datetime(2010, 9, 4, 10, 20, tzinfo=self.agenda.get_timezone())
        self.event1 = self.add_published_agenda_item(
            self.source1, 'event', 'Event1',
            sdt, sdt + relativedelta(hours=+1))
        version = self.event1.get_viewable()
        version.set_subjects(['sub'])
        version.set_target_audiences(['ta'])
        sdt = datetime(2010, 9, 10, 10, 20, tzinfo=self.agenda.get_timezone())
        self.event2 = self.add_published_agenda_item(
            self.source1, 'event2', 'Event2',
            sdt, sdt + relativedelta(days=+1))
        version = self.event2.get_viewable()
        version.set_subjects(['sub'])
        version.set_target_audiences(['ta'])

    def get_intid(self, obj):
        return getUtility(IIntIds).getId(obj)

    def test_calendar_view(self):
        status = self.browser.open('http://localhost/root/agenda')
        self.assertEquals(200, status)

    def test_calendar_view_for_event(self):
        status = self.browser.open('http://localhost/root/agenda',
                                   query={'year' : '2010',
                                          'month': '9',
                                          'day'  : '4'})
        self.assertEquals(200, status)

        xpath = '//div[@id="event_%s"]' % self.get_intid(
            self.event1.get_viewable())
        nodes = self.browser.html.xpath(xpath)
        self.assertTrue(1, len(nodes))

    def test_subscribe_view(self):
        status = self.browser.open(
            'http://localhost/root/agenda/subscribe.html')
        self.assertEquals(200, status)

    def test_ics_view(self):
        status = self.browser.open(
            'http://localhost/root/agenda/calendar.ics')
        self.assertEquals(200, status)
        intids = getUtility(IIntIds)
        uids = [intids.getId(self.event1), intids.getId(self.event2)]
        data = """BEGIN:VCALENDAR
PRODID:-//Infrae SilvaNews Calendaring//NONSGML Calendar//EN
VERSION:2.0
X-WR-CALNAME:Agenda
X-WR-TIMEZONE:Europe/Amsterdam
BEGIN:VEVENT
DTEND:20100904T092000Z
DTSTART:20100904T082000Z
SUMMARY:Event1
UID:%d@silvanews
URL:http://localhost/root/agenda/++items++%d
END:VEVENT
BEGIN:VEVENT
DTEND;VALUE=DATE:20100912
DTSTART;VALUE=DATE:20100910
SUMMARY:Event2
UID:%d@silvanews
URL:http://localhost/root/agenda/++items++%d
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n") % (uids[0], uids[0], uids[1], uids[1])
        self.assertEquals(data, self.browser.contents)


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEvent))
    suite.addTest(unittest.makeSuite(TestCalendar))
    return suite
