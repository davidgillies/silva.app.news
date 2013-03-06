# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from datetime import datetime

from Acquisition import aq_chain
from DateTime import DateTime
from Products.Silva.testing import tests
from Products.Silva.tests.test_xml_import import SilvaXMLTestCase

from silva.app.news.testing import FunctionalLayer
from silva.app.news import interfaces
from zope.interface.verify import verifyObject


class XMLImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def test_news_filter(self):
        importer = self.assertImportFile(
            'test_import_newsfilter.silvaxml',
            ['/root/export',
             '/root/export/news',
             '/root/export/filter'])
        self.assertEqual(importer.getProblems(), [])

        self.assertEqual(
            self.root.export.objectIds(),
            ['news', 'filter'])
        export = self.root.export

        self.assertTrue(verifyObject(interfaces.INewsPublication, export.news))
        self.assertTrue(verifyObject(interfaces.INewsFilter, export.filter))

        self.assertEqual(export.news.get_title(), 'News Publication')
        self.assertEqual(export.filter.get_title(), 'News Filter')
        self.assertEqual(export.filter.show_agenda_items(), False)
        self.assertEqual(export.filter.get_sources(), [export.news])
        self.assertEqual(
            map(aq_chain, export.filter.get_sources()),
            [aq_chain(export.news)])

    def test_agenda_filter(self):
        importer = self.assertImportFile(
            'test_import_agendafilter.silvaxml',
            ['/root/export',
             '/root/export/news',
             '/root/export/events',
             '/root/export/filter'])
        self.assertEqual(importer.getProblems(), [])
        self.assertEqual(
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
        importer = self.assertImportFile(
            'test_import_newsviewer.silvaxml',
            ['/root/export',
             '/root/export/news',
             '/root/export/viewer',
             '/root/export/filter'])
        self.assertEqual(importer.getProblems(), [])
        self.assertEqual(
            self.root.export.objectIds(),
            ['news', 'viewer', 'filter'])
        export = self.root.export

        self.assertTrue(verifyObject(interfaces.INewsPublication, export.news))
        self.assertTrue(verifyObject(interfaces.INewsFilter, export.filter))
        self.assertTrue(verifyObject(interfaces.INewsViewer, export.viewer))

        self.assertEqual(export.filter.show_agenda_items(), True)
        self.assertEqual(export.viewer.get_title(), 'News Viewer')
        self.assertEqual(
            export.viewer.get_filters(),
            [export.filter])
        self.assertEqual(
            map(aq_chain, export.viewer.get_filters()),
            [aq_chain(export.filter)])

    def test_agenda_viewer(self):
        importer = self.assertImportFile(
            'test_import_agendaviewer.silvaxml',
            ['/root/export',
             '/root/export/news',
             '/root/export/viewer',
             '/root/export/filter'])
        self.assertEqual(importer.getProblems(), [])
        self.assertEqual(
            self.root.export.objectIds(),
            ['news', 'viewer', 'filter'])
        export = self.root.export

        self.assertTrue(verifyObject(interfaces.INewsPublication, export.news))
        self.assertTrue(verifyObject(interfaces.IAgendaFilter, export.filter))
        self.assertTrue(verifyObject(interfaces.IAgendaViewer, export.viewer))

        self.assertEqual(export.viewer.get_title(), 'Agenda Viewer')
        self.assertEqual(
            export.viewer.get_filters(),
            [export.filter])
        self.assertEqual(
            map(aq_chain, export.viewer.get_filters()),
            [aq_chain(export.filter)])

    def test_news_item(self):
        importer = self.assertImportFile(
            'test_import_newsitem.silvaxml',
            ['/root/export',
             '/root/export/news',
             '/root/export/news/whatsup'])
        self.assertEqual(importer.getProblems(), [])
        self.assertEqual(
            self.root.export.objectIds(),
            ['news'])
        self.assertEqual(
            self.root.export.news.objectIds(),
            ['whatsup'])

        news = self.root.export.news.whatsup
        self.assertTrue(verifyObject(interfaces.INewsItem, news))
        self.assertNotEqual(news.get_editable(), None)
        self.assertEqual(news.get_viewable(), None)

        version = news.get_editable()
        self.assertTrue(verifyObject(interfaces.INewsItemVersion, version))
        self.assertEqual(version.get_subjects(), set([u'all']))
        self.assertEqual(version.get_target_audiences(), set([u'generic']))
        self.assertEqual(
            version.get_display_datetime(),
            DateTime('2010/09/30 10:00:00 GMT+2'))
        self.assertXMLEqual("""
<div>
 <h1>
  Great news everybody !
 </h1>
 <p>
  We were hired to make a new delivery.
 </p>
</div>
""", unicode(version.body))

    def test_agenda_item(self):
        importer = self.assertImportFile(
            'test_import_agendaitem.silvaxml',
            ['/root/export',
             '/root/export/news',
             '/root/export/news/event'])
        self.assertEqual(importer.getProblems(), [])

        self.assertEqual(
            self.root.export.objectIds(),
            ['news'])
        self.assertEqual(
            self.root.export.news.objectIds(),
            ['event'])

        event = self.root.export.news.event
        self.assertTrue(verifyObject(interfaces.IAgendaItem, event))
        self.assertEqual(event.get_editable(), None)
        self.assertNotEqual(event.get_viewable(), None)

        version = self.root.export.news.event.get_viewable()
        self.assertTrue(verifyObject(interfaces.IAgendaItemVersion, version))
        self.assertEqual(version.get_subjects(), set(['all']))
        self.assertEqual(version.get_target_audiences(), set(['generic']))
        self.assertEqual(
            version.get_display_datetime(),
            DateTime('2010/09/30 10:00:00 GMT+2'))

        occurrences = version.get_occurrences()
        self.assertEqual(len(occurrences), 1)

        occurrence = occurrences[0]
        self.assertEqual('America/New York', occurrence.get_timezone_name())
        timezone = occurrence.get_timezone()
        self.assertEqual(
            occurrence.get_start_datetime(),
            datetime(2010, 9, 1, 4, 0, 0, tzinfo=timezone))
        self.assertEqual('Long Long Island', occurrence.get_location())
        self.assertTrue(occurrence.is_all_day())
        self.assertEqual('FREQ=DAILY;UNTIL=20100910T123212Z',
            occurrence.get_recurrence())
        self.assertXMLEqual("""
<div>
 <h1>
  Great news everybody !
 </h1>
 <p>
  We found new broken tests to fix.
 </p>
</div>
""", unicode(version.body))

    def test_rss_aggregator(self):
        importer = self.assertImportFile(
            'test_import_rssaggregator.silvaxml',
            ['/root/export',
             '/root/export/news',
             '/root/export/empty'])
        self.assertEqual(importer.getProblems(), [])
        self.assertEqual(
            self.root.export.objectIds(),
            ['news', 'empty'])

        rss = self.root.export.news
        rss_empty = self.root.export.empty
        self.assertTrue(verifyObject(interfaces.IRSSAggregator, rss))
        self.assertTrue(verifyObject(interfaces.IRSSAggregator, rss_empty))
        self.assertEqual(rss.get_title(), 'Latest Ubernet news')
        self.assertEqual(rss.get_feeds(), ['bar', 'foo'])

        self.assertEqual(rss_empty.get_title(), 'Nothing to see here')
        self.assertEqual(rss_empty.get_feeds(), [])

    def test_news_publication(self):
        # A news pub with a viewer (index) a filter (filter) customized
        # A news item, an agenda item, agenda viewer and agenda filter.
        importer = self.assertImportFile(
            'test_import_newspublication.silvaxml',
            ['/root/news/index',
             '/root/news/the_empire_falls',
             '/root/news/lolcats_attacks',
             '/root/news/events',
             '/root/news/filter',
             '/root/news/filter_events',
             '/root/news'])

        news = self.root._getOb('news', None)
        self.assertTrue(verifyObject(interfaces.INewsPublication, news))
        self.assertEqual(
            self.root.news.objectIds(),
            ['index',
             'the_empire_falls',
             'lolcats_attacks',
             'events',
             'filter',
             'filter_events'])
        # Verify content
        self.assertTrue(verifyObject(interfaces.INewsViewer, news.index))
        self.assertTrue(verifyObject(interfaces.INewsFilter, news.filter))
        self.assertTrue(verifyObject(interfaces.IAgendaViewer, news.events))
        self.assertTrue(verifyObject(interfaces.IAgendaFilter, news.filter_events))
        self.assertEqual(
            importer.getProblems(),
            [(u'Broken source in import: External Source cs_you_tube is not available.',
              news.lolcats_attacks.get_viewable())])

        # Verify setup
        tests.assertContentItemsEqual(
            news.filter.get_sources(),
            [news])
        tests.assertContentItemsEqual(
            news.index.get_filters(),
            [news.filter])
        tests.assertContentItemsEqual(
            news.filter_events.get_sources(),
            [news])
        tests.assertContentItemsEqual(
            news.events.get_filters(),
            [news.filter_events])
        self.assertItemsEqual(
            [b.getPath() for b in news.index.get_items()],
            ['/root/news/the_empire_falls/0', '/root/news/lolcats_attacks/0'])
        self.assertItemsEqual(
            [b.getPath() for b in news.events.get_items_by_date(7, 2012)],
            ['/root/news/lolcats_attacks/0'])
        self.assertItemsEqual(
            [b.getPath() for b in news.events.get_items()],
            [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    return suite
