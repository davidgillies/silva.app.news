# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from datetime import datetime

from Products.Silva.silvaxml import xmlexport
from Products.Silva.tests.test_xml_export import SilvaXMLTestCase

from silva.core.interfaces import IPublicationWorkflow
from silva.app.news.AgendaItem import AgendaItemOccurrence
from silva.app.news.testing import FunctionalLayer
from silva.core.interfaces.errors import ExternalReferenceError


class XMLExportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        super(XMLExportTestCase, self).setUp()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('export', 'Export Folder')

    def test_news_filter(self):
        """Add a filter and a news publication at root level and export
        the filter.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory.manage_addNewsFilter('filter', 'News Filter')
        self.root.export.filter.set_sources([self.root.export.news])

        xml, info = xmlexport.exportToString(self.root.export)
        self.assertExportEqual(
            xml, 'test_export_newsfilter.silvaxml', globs=globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_news_filter_external_reference(self):
        """Add a filter and a news publication and export only the
        filter.
        """
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsFilter('filter', 'News Filter')
        self.root.export.filter.set_sources([self.root.news])

        with self.assertRaises(ExternalReferenceError):
            xml, info = xmlexport.exportToString(self.root.export)

    def test_agenda_filter(self):
        """Add a filter and a news publication at root level and export
        the filter.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory.manage_addAgendaFilter('filter', 'Agenda Filter')
        self.root.export.filter.add_source(self.root.export.news)

        xml, info = xmlexport.exportToString(self.root.export)
        self.assertExportEqual(
            xml, 'test_export_agendafilter.silvaxml', globs=globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_news_viewer(self):
        """Export a news viewer.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory.manage_addNewsFilter('filter', 'News Filter')
        factory.manage_addNewsViewer('viewer', 'News Viewer')
        self.root.export.filter.set_sources([self.root.export.news])
        self.root.export.viewer.set_filters([self.root.export.filter])
        xml, info = xmlexport.exportToString(self.root.export)
        self.assertExportEqual(
            xml, 'test_export_newsviewer.silvaxml', globs=globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_agenda_viewer(self):
        """Export an agenda viewer.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory.manage_addAgendaFilter('filter', 'Agenda Filter')
        factory.manage_addAgendaViewer('viewer', 'Agenda Viewer')
        self.root.export.filter.set_sources([self.root.export.news])
        self.root.export.viewer.set_filters([self.root.export.filter])
        xml, info = xmlexport.exportToString(self.root.export)
        self.assertExportEqual(
            xml, 'test_export_agendaviewer.silvaxml', globs=globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_news_item(self):
        """Export a news item.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory = self.root.export.news.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('news', 'Some news')

        version = self.root.export.news.news.get_editable()
        self.assertTrue(version)
        version.set_subjects(['all'])
        version.set_target_audiences(['generic'])
        version.set_display_datetime(datetime(2010, 9, 30, 10, 0, 0))
        xml, info = xmlexport.exportToString(self.root.export)
        self.assertExportEqual(
            xml, 'test_export_newsitem.silvaxml', globs=globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_agenda_item(self):
        """Export an agenda item.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory = self.root.export.news.manage_addProduct['silva.app.news']
        factory.manage_addAgendaItem('event', 'Some event')

        version = self.root.export.news.event.get_editable()
        self.assertIsNot(version, None)
        version.body.save_raw_text('<p>Good news!</p><p>I fixed the tests.</p>')
        version.set_occurrences([
                AgendaItemOccurrence(
                    location='Rotterdam',
                    recurrence='FREQ=DAILY;UNTIL=20100910T123212Z',
                    timezone_name='Europe/Amsterdam',
                    all_day=True,
                    start_datetime=datetime(2010, 9, 1, 10, 0, 0))])
        version.set_subjects(['all'])
        version.set_target_audiences(['generic'])
        version.set_display_datetime(datetime(2010, 9, 30, 10, 0, 0))
        self.layer.login('editor')
        IPublicationWorkflow(self.root.export.news.event).publish()

        xml, info = xmlexport.exportToString(self.root.export)
        self.assertExportEqual(
            xml, 'test_export_agendaitem.silvaxml', globs=globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_rss_aggregator(self):
        """Export an RSS agregator.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addRSSAggregator('rss', 'RSS Feeds')
        self.root.export.rss.set_feeds([
                'http://infrae.com/news/atom.xml',
                'http://pypi.python.org/pypi?%3Aaction=rss'])

        xml, info = xmlexport.exportToString(self.root.export)
        self.assertExportEqual(
            xml, 'test_export_rssaggregator.silvaxml', globs=globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLExportTestCase))
    return suite
