# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from datetime import datetime
from Acquisition import aq_chain
from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from silva.app.news.testing import FunctionalLayer
from silva.app.news import interfaces
from silva.core.interfaces.events import IContentImported
from zope.interface.verify import verifyObject


class XMLImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def test_news_filter(self):
        self.import_file('test_import_newsfilter.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/export',
             'ContentImported for /root/export/news',
             'ContentImported for /root/export/filter'],
            IContentImported)

        self.assertEquals(
            self.root.export.objectIds(),
            ['news', 'filter'])
        export = self.root.export

        self.assertTrue(verifyObject(interfaces.INewsPublication, export.news))
        self.assertTrue(verifyObject(interfaces.INewsFilter, export.filter))

        self.assertEqual(export.news.get_title(), 'News Publication')
        self.assertEqual(export.filter.get_title(), 'News Filter')
        self.assertEqual(export.filter.get_sources(), [export.news])
        self.assertEqual(
            map(aq_chain, export.filter.get_sources()),
            [aq_chain(export.news)])

    def test_agenda_filter(self):
        self.import_file('test_import_agendafilter.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/export',
             'ContentImported for /root/export/news',
             'ContentImported for /root/export/events',
             'ContentImported for /root/export/filter'],
            IContentImported)

        self.assertEquals(
            self.root.export.objectIds(),
            ['news', 'filter', 'events'])
        export = self.root.export

        self.assertTrue(verifyObject(interfaces.INewsPublication, export.news))
        self.assertTrue(verifyObject(interfaces.IAgendaFilter, export.filter))

        self.assertEqual(export.news.get_title(), 'News Publication')
        self.assertEqual(export.filter.get_title(), 'Agenda Filter')
        self.assertEqual(
            export.filter.get_sources(),
            [export.news, export.events])
        self.assertEqual(
            map(aq_chain, export.filter.get_sources()),
            [aq_chain(export.news), aq_chain(export.events)])

    def test_news_viewer(self):
        self.import_file('test_import_newsviewer.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/export',
             'ContentImported for /root/export/news',
             'ContentImported for /root/export/viewer',
             'ContentImported for /root/export/filter'],
            IContentImported)

        self.assertEquals(
            self.root.export.objectIds(),
            ['news', 'viewer', 'filter'])
        export = self.root.export

        self.assertTrue(verifyObject(interfaces.INewsPublication, export.news))
        self.assertTrue(verifyObject(interfaces.INewsFilter, export.filter))
        self.assertTrue(verifyObject(interfaces.INewsViewer, export.viewer))

        self.assertEqual(export.viewer.get_title(), 'News Viewer')
        self.assertEqual(
            export.viewer.get_filters(),
            [export.filter])
        self.assertEqual(
            map(aq_chain, export.viewer.get_filters()),
            [aq_chain(export.filter)])

    def test_agenda_viewer(self):
        assert False

    def test_news_item(self):
        self.import_file('test_import_newsitem.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/document'],
            IContentImported)

        self.assertTrue(hasattr(self.root.export, 'newspub'))
        self.assertTrue(hasattr(self.root.export.newspub, 'news'))
        news = self.root.export.newspub.news
        version = news.get_editable()
        self.assertEquals(['all'], version.get_subjects())
        self.assertEquals(['generic'], version.get_target_audiences())
        self.assertEquals(
            datetime(2010, 9, 30, 10, 0, 0),
            version.get_display_datetime())

    def test_agenda_item(self):
        self.import_file('test_import_agendaitem.silvaxml', globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/document'],
            IContentImported)

        self.assertTrue(hasattr(self.root.export, 'newspub'))
        self.assertTrue(hasattr(self.root.export.newspub, 'event'))
        version = self.root.export.newspub.event.get_viewable()

        self.assertEquals('Europe/Amsterdam', version.get_timezone_name())
        timezone = version.get_timezone()
        self.assertEquals(datetime(2010, 9, 1, 10, 0, 0, tzinfo=timezone),
            version.get_start_datetime())
        self.assertEquals('Rotterdam', version.get_location())
        self.assertTrue(version.is_all_day())
        self.assertEquals(['all'], version.get_subjects())
        self.assertEquals(['generic'], version.get_target_audiences())
        self.assertEquals('FREQ=DAILY;UNTIL=20100910T123212Z',
            version.get_recurrence())
        self.assertEquals('Europe/Amsterdam', version.get_timezone_name())
        self.assertEquals(
            datetime(2010, 9, 30, 10, 0, 0),
            version.get_display_datetime())

    def test_rss_aggregator(self):
        assert False

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    return suite
