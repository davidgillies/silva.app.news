# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from datetime import datetime

from Products.Silva.silvaxml import xmlexport
from Products.Silva.tests.helpers import publish_object
from Products.Silva.tests.test_xml_export import SilvaXMLTestCase
from silva.app.news.datetimeutils import get_timezone
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

        xml, info = xmlexport.exportToString(self.root.export)
        self.assertExportEqual(
            xml, 'test_export_newsfilter.silvaxml', globs=globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

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
        self.assertTrue(version)
        version.set_location('Rotterdam')
        version.set_subjects(['all'])
        version.set_target_audiences(['generic'])
        version.set_recurrence('FREQ=DAILY;UNTIL=20100910T123212Z')
        timezone = get_timezone('Europe/Amsterdam')
        version.set_timezone_name('Europe/Amsterdam')
        version.set_start_datetime(
            datetime(2010, 9, 1, 10, 0, 0, tzinfo=timezone))
        version.set_all_day(True)
        version.set_display_datetime(datetime(2010, 9, 30, 10, 0, 0))
        publish_object(self.root.export.news.event)

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
