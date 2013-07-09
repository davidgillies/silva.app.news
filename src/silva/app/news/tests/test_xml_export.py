# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from datetime import datetime

from Products.Silva.tests.test_xml_export import SilvaXMLTestCase

from silva.core.interfaces import IPublicationWorkflow
from silva.app.news.AgendaItem import AgendaItemOccurrence
from silva.app.news.testing import FunctionalLayer


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

        exporter = self.assertExportEqual(
            self.root.export,
            'test_export_newsfilter.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

    def test_news_filter_external_reference(self):
        """Add a filter and a news publication and export only the
        filter.
        """
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsFilter('filter', 'News Filter')
        self.root.export.filter.set_sources([self.root.news])
        self.assertExportFail(self.root.export)

    def test_agenda_filter(self):
        """Add a filter and a news publication at root level and export
        the filter.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory.manage_addAgendaFilter('filter', 'Agenda Filter')
        self.root.export.filter.add_source(self.root.export.news)

        exporter = self.assertExportEqual(
            self.root.export,
            'test_export_agendafilter.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

    def test_news_viewer(self):
        """Export a news viewer.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory.manage_addNewsFilter('filter', 'News Filter')
        factory.manage_addNewsViewer('viewer', 'News Viewer')
        self.root.export.filter.set_sources([self.root.export.news])
        self.root.export.viewer.set_filters([self.root.export.filter])
        self.root.export.viewer.set_number_is_days(True)
        self.root.export.viewer.set_number_to_show(10)

        exporter = self.assertExportEqual(
            self.root.export,
            'test_export_newsviewer.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

    def test_news_viewer_external(self):
        """Export a news viewer that refer a filter that is outside of
        the export folder.
        """
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsFilter('filter', 'News Filter')
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory.manage_addNewsFilter('filter', 'News Filter')
        factory.manage_addNewsViewer('viewer', 'News Viewer')
        self.root.export.filter.set_sources(
            [self.root.export.news])
        self.root.export.viewer.set_filters(
            [self.root.export.filter, self.root.filter])

        self.assertExportFail(self.root.export)

    def test_news_viewer_external_force(self):
        """Export a news viewer that refer a filter that is outside of
        the export folder, with the option external_references set to True.
        """
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsFilter('filter', 'News Filter')
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory.manage_addNewsFilter('filter', 'News Filter')
        factory.manage_addNewsViewer('viewer', 'News Viewer')
        self.root.export.filter.set_sources(
            [self.root.export.news])
        self.root.export.viewer.set_filters(
            [self.root.export.filter, self.root.filter])

        exporter = self.assertExportEqual(
            self.root.export,
            'test_export_newsviewer_external.silvaxml',
            options={'external_references': True})
        self.assertEqual(
            exporter.getZexpPaths(),
            [])
        self.assertEqual(
            exporter.getAssetPaths(),
            [])
        self.assertEqual(
            exporter.getProblems(),
            [(u'Content contains 1 reference(s) pointing outside of the export.',
              self.root.export.viewer)])

    def test_agenda_viewer(self):
        """Export an agenda viewer.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News Publication')
        factory.manage_addAgendaFilter('filter', 'Agenda Filter')
        factory.manage_addAgendaViewer('viewer', 'Agenda Viewer')
        self.root.export.filter.set_sources([self.root.export.news])
        self.root.export.viewer.set_filters([self.root.export.filter])

        exporter = self.assertExportEqual(
            self.root.export,
            'test_export_agendaviewer.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

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

        exporter = self.assertExportEqual(
            self.root.export,
            'test_export_newsitem.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

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

        exporter = self.assertExportEqual(
            self.root.export,
            'test_export_agendaitem.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

    def test_rss_aggregator(self):
        """Export an RSS agregator.
        """
        factory = self.root.export.manage_addProduct['silva.app.news']
        factory.manage_addRSSAggregator('rss', 'RSS Feeds')
        self.root.export.rss.set_feeds([
                'http://infrae.com/news/atom.xml',
                'http://pypi.python.org/pypi?%3Aaction=rss'])

        exporter = self.assertExportEqual(
            self.root.export,
            'test_export_rssaggregator.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLExportTestCase))
    return suite
