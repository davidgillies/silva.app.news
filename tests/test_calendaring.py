from icalendar.interfaces import IEvent, ICalendar
from icalendar import Event
import SilvaNewsTestCase
from datetime import datetime, timedelta
from zope.component import getAdapter


class TestEvent(SilvaNewsTestCase.SilvaNewsTestCase):

    def afterSetUp(self):
        super(TestEvent, self).afterSetUp()

    def test_event_generation(self):
        start = datetime.now()
        self.add_published_agenda_item(self.root, 'ai1',
            'Agenda Item', start, start + timedelta(60))
        agenda_item = getattr(self.root, 'ai1')
        version = getattr(agenda_item, '0')
        event = IEvent(version)
        read_event = Event.from_string(str(event))


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEvent))
    suite.addTest(unittest.makeSuite(TestCalendar))
    return suite
