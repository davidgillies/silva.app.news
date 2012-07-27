# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from datetime import datetime

from Acquisition import aq_chain
from DateTime import DateTime
from Products.Silva.tests.test_xml_import import SilvaXMLTestCase

from silva.app.news.testing import FunctionalLayer
from silva.app.news import interfaces
from silva.core.interfaces.events import IContentImported
from zope.interface.verify import verifyObject


class XMLImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def test_news_filter(self):
        self.import_file(
            'test_import_newsfilter.silvaxml',
            globs=globals())
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
        self.assertEqual(export.filter.show_agenda_items(), False)
        self.assertEqual(export.filter.get_sources(), [export.news])
        self.assertEqual(
            map(aq_chain, export.filter.get_sources()),
            [aq_chain(export.news)])

    def test_agenda_filter(self):
        self.import_file(
            'test_import_agendafilter.silvaxml',
            globs=globals())
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
        self.import_file(
            'test_import_newsviewer.silvaxml',
            globs=globals())
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

        self.assertEqual(export.filter.show_agenda_items(), True)
        self.assertEqual(export.viewer.get_title(), 'News Viewer')
        self.assertEqual(
            export.viewer.get_filters(),
            [export.filter])
        self.assertEqual(
            map(aq_chain, export.viewer.get_filters()),
            [aq_chain(export.filter)])

    def test_agenda_viewer(self):
        self.import_file(
            'test_import_agendaviewer.silvaxml',
            globs=globals())
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
        self.import_file(
            'test_import_newsitem.silvaxml',
            globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/export',
             'ContentImported for /root/export/news',
             'ContentImported for /root/export/news/whatsup'],
            IContentImported)

        self.assertEqual(
            self.root.export.objectIds(),
            ['news'])
        self.assertEqual(
            self.root.export.news.objectIds(),
            ['index', 'filter', 'whatsup'])

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
        self.import_file(
            'test_import_agendaitem.silvaxml',
            globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/export',
             'ContentImported for /root/export/news',
             'ContentImported for /root/export/news/event'],
            IContentImported)

        self.assertEqual(
            self.root.export.objectIds(),
            ['news'])
        self.assertEqual(
            self.root.export.news.objectIds(),
            ['index', 'filter', 'event'])

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
        self.import_file(
            'test_import_rssaggregator.silvaxml',
            globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/export',
             'ContentImported for /root/export/news',
             'ContentImported for /root/export/empty'],
            IContentImported)

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
        self.import_file(
            'test_import_newspublication.silvaxml',
            globs=globals())
        self.assertEventsAre(
            ['ContentImported for /root/news/index',
             'ContentImported for /root/news/the_empire_falls',
             'ContentImported for /root/news/lolcats_attacks',
             'ContentImported for /root/news/events',
             'ContentImported for /root/news/filter',
             'ContentImported for /root/news/filter_events',
             'ContentImported for /root/news'],
            IContentImported)

        assert False, "TBD"

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    return suite
