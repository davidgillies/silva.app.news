import unittest
from icalendar import vDatetime
from DateTime import DateTime
from datetime import datetime
from dateutil.relativedelta import relativedelta

from zope.component import getUtility

from Products.SilvaNews.datetimeutils import (
    datetime_to_unixtimestamp, get_timezone)
from Products.SilvaNews.tests.SilvaNewsTestCase import FunctionalLayer
from silva.core.services.interfaces import ICatalogService


class TestAgendaItemRecurrence(unittest.TestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_create_agenda_item_without_recurrence(self):
        agenda_item = self.create_agenda_item()
        version = agenda_item.get_editable()
        dt = datetime(2010, 10, 9, 10, 1)
        version.set_start_datetime(dt)
        version.set_end_datetime(dt + relativedelta(hours=+2))
        self.assertEquals(None, version.get_rrule())

    def test_create_agenda_item_with_recurrence(self):
        agenda_item = self.create_agenda_item()
        version = agenda_item.get_editable()
        version.set_timezone_name('Europe/Amsterdam')
        dt = datetime(2010, 9, 10, 10, 0, tzinfo=version.get_timezone())
        version.set_start_datetime(dt)
        version.set_end_datetime(dt + relativedelta(hours=+2))
        # every two weeks
        version.set_recurrence(
            'FREQ=WEEKLY;INTERVAL=2;BYDAY=FR;UNTIL=%s' %
            vDatetime(dt + relativedelta(months=+1)))
        recurrence = version.get_rrule()
        self.assertNotEquals(None, recurrence)
        tz = get_timezone('Europe/Amsterdam')
        self.assertEquals(
            [datetime(2010, 9, 10, 10, 0, tzinfo=tz),
             datetime(2010, 9, 24, 10, 0, tzinfo=tz),
             datetime(2010, 10, 8, 10, 0, tzinfo=tz)],
            list(recurrence))
        calendar_date = version.get_calendar_datetime()
        ranges = calendar_date.get_datetime_ranges()
        self.assertEquals(
            [(datetime(2010, 9, 10, 10, 0, tzinfo=tz),
              datetime(2010, 9, 10, 12, 0, tzinfo=tz)),
             (datetime(2010, 9, 24, 10, 0, tzinfo=tz),
              datetime(2010, 9, 24, 12, 0, tzinfo=tz)),
             (datetime(2010, 10, 8, 10, 0, tzinfo=tz),
              datetime(2010, 10, 8, 12, 0, tzinfo=tz))],
            ranges)

    def test_catalog(self):
        agenda_item = self.create_agenda_item()
        version = agenda_item.get_editable()
        version.set_timezone_name('Europe/Amsterdam')
        dt = datetime(2010, 9, 10, 10, 0, tzinfo=version.get_timezone())
        version.set_start_datetime(dt)
        version.set_end_datetime(dt + relativedelta(hours=+2))
        # every two weeks
        version.set_recurrence(
            'FREQ=WEEKLY;INTERVAL=2;BYDAY=FR;UNTIL=%s' %
            vDatetime(dt + relativedelta(months=+1)))
        # last for one month
        recurrence = version.get_rrule()
        self.assertNotEquals(None, recurrence)
        tz = get_timezone('Europe/Amsterdam')

        agenda_item.set_unapproved_version_publication_datetime(DateTime())
        agenda_item.approve_version()

        catalog = getUtility(ICatalogService)
        start = datetime_to_unixtimestamp(
            datetime(2010, 9, 10, 0, 0, tzinfo=tz))
        end = datetime_to_unixtimestamp(
            datetime(2010, 9, 10, 23, 59, tzinfo=tz))

        def search():
            return map(lambda x: x.getObject(),
                       catalog({'idx_timestamp_ranges': [start, end]}))

        self.assertEquals([version], search())

        start = datetime_to_unixtimestamp(
            datetime(2010, 9, 24, 10, 0, tzinfo=tz))
        end = datetime_to_unixtimestamp(
            datetime(2010, 9, 24, 12, 0, tzinfo=tz))
        self.assertEquals([version], search())

        start = datetime_to_unixtimestamp(
            datetime(2010, 10, 8, 11, 0, tzinfo=tz))
        end = datetime_to_unixtimestamp(
            datetime(2010, 10, 8, 13, 0, tzinfo=tz))
        self.assertEquals([version], search())

    def create_agenda_item(self):
        factory = self.root.manage_addProduct['Products.SilvaNews']
        factory.manage_addPlainAgendaItem('event', 'Event')
        return self.root.event


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAgendaItemRecurrence))
    return suite
