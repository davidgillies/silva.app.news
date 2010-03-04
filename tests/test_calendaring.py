from icalendar.interfaces import IEvent, ICalendar
from icalendar import Event
import SilvaNewsTestCase
from datetime import datetime, timedelta
from Products.SilvaNews.datetimeutils import local_timezone, datetime_to_unixtimestamp
from zope.component import getAdapter


class TestEvent(SilvaNewsTestCase.SilvaNewsTestCase):

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


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEvent))
    return suite
