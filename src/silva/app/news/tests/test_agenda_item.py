# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# coding=utf-8

from datetime import datetime
import unittest

from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.ftesting import public_settings
from Products.Silva.testing import tests

from silva.core.interfaces import IPublicationWorkflow
from silva.app.news.interfaces import IAgendaItem, IAgendaItemVersion
from silva.app.news.interfaces import IServiceNews
from silva.app.news.testing import FunctionalLayer, get_identifier
from silva.app.news.AgendaItem.content import AgendaItemOccurrence

def format_date(date):
    return date.utcdatetime().strftime('%Y%m%dT%H%M%SZ')


class AgendaItemTestCase(unittest.TestCase):
    """Test the AgendaItem content type.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_item(self):
        factory = self.root.manage_addProduct['silva.app.news']
        with tests.assertTriggersEvents('ContentCreatedEvent'):
            factory.manage_addAgendaItem('event', 'Testing event')
        event = self.root._getOb('event', None)
        self.assertTrue(verifyObject(IAgendaItem, event))
        version = event.get_editable()
        self.assertTrue(verifyObject(IAgendaItemVersion, version))
        version.set_subjects(['invalid', 'other', 'root'])
        self.assertEqual(version.get_subjects(), set(['root']))
        version.set_target_audiences(['generic', 'root'])
        self.assertEqual(version.get_target_audiences(), set(['root']))

        service = getUtility(IServiceNews)
        service.add_subject('other', 'Other')
        service.add_target_audience('generic', 'Generic')
        self.assertEqual(version.get_subjects(), set(['other', 'root']))
        self.assertEqual(version.get_target_audiences(), set(['generic', 'root']))


class RenderAgendaItemTestCase(unittest.TestCase):
    """Test the rendering of an AgendaItem.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addAgendaItem('testing', u'Test aléatoire')
        tzinfo = getUtility(IServiceNews).default_timezone()
        version = self.root.testing.get_editable()
        version.set_external_url('http://silvacms.org')
        version.set_occurrences([
                AgendaItemOccurrence(
                    start_datetime=datetime(2012, 7, 31, 10, 00, tzinfo=tzinfo),
                    end_datetime=datetime(2012, 7, 31, 18, 00, tzinfo=tzinfo))])

        IPublicationWorkflow(self.root.testing).publish()

    def test_rendering(self):
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(browser.open('/root/testing'), 200)
            self.assertEqual(browser.inspect.title, [u'Test aléatoire', ])

    def test_ics(self):
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(browser.open('/root/testing/event.ics'), 200)
            self.assertEqual(
                browser.content_type,
                'text/calendar;charset=utf-8')
            self.assertMultiLineEqual(
                browser.contents.replace("\r\n", "\n"),
                u"""BEGIN:VCALENDAR
PRODID:-//Silva News Calendaring//lonely event//
VERSION:2.0
BEGIN:VEVENT
CREATED:%(created)s
DTEND:20120731T160000Z
DTSTART:20120731T080000Z
LAST-MODIFIED:%(modified)s
SUMMARY:Test aléatoire
UID:%(identifier)s@0@silvanews
URL:http://localhost/root/testing
END:VEVENT
END:VCALENDAR
""" % {'identifier': get_identifier(self.root.testing.get_viewable()),
       'created': format_date(self.root.testing.get_creation_datetime()),
       'modified': format_date(self.root.testing.get_modification_datetime())})


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AgendaItemTestCase))
    suite.addTest(unittest.makeSuite(RenderAgendaItemTestCase))
    return suite
