import json
import unittest
import operator

from datetime import datetime
from dateutil.relativedelta import relativedelta

from silva.app.news.testing import get_identifier
from silva.app.news.tests.SilvaNewsTestCase import SilvaNewsTestCase


class TestJsonEventsAPI(SilvaNewsTestCase):
    maxDiff = None

    def setUp(self):
        super(TestJsonEventsAPI, self).setUp()
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addAgendaFilter('filter', 'Agenda Filter')
        factory.manage_addAgendaViewer('agenda', 'Agenda Viewer')
        factory.manage_addNewsPublication('events', 'Events Publication')

        self.root.filter.set_sources([self.root.events])
        self.root.agenda.set_filters([self.root.filter])
        self.root.agenda.set_timezone_name('Europe/Amsterdam')

        timezone = self.root.agenda.get_timezone()

        sdt = datetime(2010, 9, 4, 10, 20, tzinfo=timezone)
        self.add_published_agenda_item(
            self.root.events, 'culture', 'Cultural event',
            sdt, sdt + relativedelta(hours=+1))

        sdt = datetime(2010, 9, 10, 10, 20, tzinfo=timezone)
        self.add_published_agenda_item(
            self.root.events, 'fishing', 'Fishing event',
            sdt, sdt + relativedelta(days=+1))
        self.add_published_agenda_item(
            self.root.events, 'hunting', 'Hunting event',
            sdt.replace(month=8), sdt.replace(month=8, day=9))

    def test_empty_request(self):
        """json events without start and end returns empty list"""
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('/root/agenda/++rest++silva.app.news.events'),
                200)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertEqual(
                json.loads(browser.contents),
                [])

    def test_json_results(self):
        """json events returns only the agenda items within the range"""
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open(
                    '/root/agenda/++rest++silva.app.news.events',
                    form={'start': datetime(2010, 9, 1).strftime("%s"),
                          'end': datetime(2010, 9, 30).strftime("%s")}),
                200)
            data = json.loads(browser.contents)
            data.sort(key=operator.itemgetter('title'))

            # Hunting is not in the corresponding timezone.
            self.assertEqual(
                data,
                [{u'allDay': False,
                  u'className': u'fullcalendar-agenda-item',
                  u'end': 1283592000,
                  u'id': u'agenda-item-%s-0' % get_identifier(
                            self.root.events.culture.get_viewable()),
                  u'start': 1283588400,
                  u'title': u'Cultural event',
                  u'url': u'http://localhost/root/events/culture'},
                 {u'allDay': False,
                  u'className': u'fullcalendar-agenda-item',
                  u'end': 1284193200,
                  u'id': u'agenda-item-%s-0' % get_identifier(
                            self.root.events.fishing.get_viewable()),
                  u'start': 1284106800,
                  u'title': u'Fishing event',
                  u'url': u'http://localhost/root/events/fishing'}])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestJsonEventsAPI))
    return suite

