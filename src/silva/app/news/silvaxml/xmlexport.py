# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok
from zope.interface import Interface

from silva.app.news import interfaces
from silva.app.news.datetimeutils import utc_datetime
from silva.app.news.silvaxml import NS_NEWS_URI
from silva.core.editor.transform.silvaxml.xmlexport import TextProducerProxy
from silva.core.references.utils import canonical_path
from silva.core.references.utils import is_inside_container
from silva.core.references.utils import relative_path
from silva.core.xml import producers


def iso_datetime(dt):
    if dt:
        string = utc_datetime(dt).replace(microsecond=0).isoformat()
        if string.endswith('+00:00'):
            string = string[:-6] + 'Z'
        return string
    return ''


class NewsPublicationProducer(producers.SilvaContainerProducer):
    """Export a News Publication object to XML.
    """
    grok.adapts(interfaces.INewsPublication, Interface)

    def sax(self):
        self.startElementNS(
            NS_NEWS_URI, 'news_publication', {'id': self.context.id})
        self.sax_metadata()
        self.sax_contents()
        self.endElementNS(NS_NEWS_URI,'news_publication')


class RSSAggregatorProducer(producers.SilvaProducer):
     """Export a RSSAggregator object to XML.
     """
     grok.adapts(interfaces.IRSSAggregator, Interface)

     def sax(self):
         self.startElementNS(
             NS_NEWS_URI, 'rss_aggregator', {'id': self.context.id})
         self.sax_metadata()
         for feed in self.context.get_feeds():
             self.startElementNS(NS_NEWS_URI, 'url')
             self.characters(feed)
             self.endElementNS(NS_NEWS_URI, 'url')
         self.endElementNS(NS_NEWS_URI, 'rss_aggregator')


class NewsFilterProducer(producers.SilvaProducer):
    """Export a NewsFilter object to XML.
    """
    grok.adapts(interfaces.INewsFilter, Interface)

    def sax(self):
        self.startElementNS(
            NS_NEWS_URI,
            'news_filter',
            {'id': self.context.id,
             'target_audiences': ','.join(self.context.get_target_audiences()),
             'subjects': ','.join(self.context.get_subjects()),
             'show_agenda_items': str(self.context.show_agenda_items())})
        self.sax_metadata()
        self.startElement('content')
        self.sax_sources()
        self.sax_excludes()
        self.endElement('content')
        self.endElementNS(NS_NEWS_URI,'news_filter')

    def sax_sources(self):
        self.startElementNS(NS_NEWS_URI, "sources")
        for path in self.get_references("sources"):
            self.startElementNS(NS_NEWS_URI, 'source', {'target': path})
            self.endElementNS(NS_NEWS_URI, 'source')
        self.endElementNS(NS_NEWS_URI, "sources")

    def sax_excludes(self):
        self.startElementNS(NS_NEWS_URI, "excludes")
        exported = self.getExported()
        for item in self.context.get_excluded_items():
            if is_inside_container(exported.root, item):
                path = [exported.root.getId()] + relative_path(
                    exported.rootPath, item.getPhysicalPath())
                path = canonical_path('/'.join(path))
                self.startElementNS(
                    NS_NEWS_URI, 'exclude', {'target': path})
                self.endElementNS(NS_NEWS_URI, 'exclude')
            else:
                exported.reportProblem(
                    'Content excluded from the filter was not exported',
                    content=self.context)
        self.endElementNS(NS_NEWS_URI, "excludes")


class AgendaFilterProducer(NewsFilterProducer):
    """Export a AgendaFilter object to XML.
    """
    grok.adapts(interfaces.IAgendaFilter, Interface)

    def sax(self):
        self.startElementNS(
            NS_NEWS_URI,
            'agenda_filter',
            {'id': self.context.id,
             'target_audiences': ','.join(self.context.get_target_audiences()),
             'subjects': ','.join(self.context.get_subjects())})
        self.sax_metadata()
        self.startElement('content')
        self.sax_sources()
        self.sax_excludes()
        self.endElement('content')
        self.endElementNS(NS_NEWS_URI,'agenda_filter')


class NewsViewerProducer(producers.SilvaProducer):
    """Export a NewsViewer object to XML.
    """
    grok.adapts(interfaces.INewsViewer, Interface)

    def sax(self):
        self.startElementNS(
            NS_NEWS_URI,
            'news_viewer',
            {'id': self.context.id,
             'number_to_show': str(self.context.get_number_to_show()),
             'number_to_show_archive': str(
                    self.context.get_number_to_show_archive()),
             'hide_expired_events': str(
                 self.context.get_hide_expired_events()),
             'number_is_days': str(self.context.get_number_is_days())})
        self.sax_metadata()
        self.startElement('content')
        self.sax_filters()
        self.endElement('content')
        self.endElementNS(NS_NEWS_URI,'news_viewer')

    def sax_filters(self):
        self.startElementNS(NS_NEWS_URI, "filters")
        for path in self.get_references("filters"):
            self.startElementNS(NS_NEWS_URI, 'filter', {'target': path})
            self.endElementNS(NS_NEWS_URI, 'filter')
        self.endElementNS(NS_NEWS_URI, "filters")


class AgendaViewerProducer(NewsViewerProducer):
     """Export a AgendaViewer object to XML."""
     grok.adapts(interfaces.IAgendaViewer, Interface)

     def sax(self):
        self.startElementNS(
            NS_NEWS_URI,
            'agenda_viewer',
            {'id': self.context.id,
             'number_to_show': str(self.context.get_number_to_show()),
             'number_to_show_archive': str(
                    self.context.get_number_to_show_archive()),
             'number_is_days': str(self.context.get_number_is_days())})
        self.sax_metadata()
        self.startElement('content')
        self.sax_filters()
        self.endElement('content')
        self.endElementNS(NS_NEWS_URI,'agenda_viewer')


class NewsItemProducer(producers.SilvaVersionedContentProducer):
    """Export a NewsItem object to XML.
    """
    grok.adapts(interfaces.INewsItem, Interface)

    def sax(self):
        """sax"""
        self.startElementNS(
            NS_NEWS_URI, 'news_item', {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElementNS(NS_NEWS_URI,'news_item')


class NewsItemVersionProducer(producers.SilvaProducer):
    """Export a version of a NewsItem object to XML.
    """
    grok.adapts(interfaces.INewsItemVersion, Interface)

    def sax(self):
        """sax"""
        self.startElement(
            'content',
            {'version_id': self.context.id,
             'subjects': ','.join(self.context.get_subjects()),
             'target_audiences': ','.join(self.context.get_target_audiences()),
             'display_datetime': iso_datetime(
                    self.context.get_display_datetime())})
        self.sax_metadata()
        self.sax_content()
        self.endElement('content')

    def sax_content(self):
        self.startElementNS(NS_NEWS_URI, 'body')
        TextProducerProxy(self.context, self.context.body).sax(self)
        self.endElementNS(NS_NEWS_URI, 'body')


class AgendaItemProducer(producers.SilvaVersionedContentProducer):
    """Export an AgendaItem object to XML.
    """
    grok.adapts(interfaces.IAgendaItem, Interface)

    def sax(self):
        """sax"""
        self.startElementNS(
            NS_NEWS_URI, 'agenda_item', {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElementNS(NS_NEWS_URI,'agenda_item')


class AgendaItemVersionProducer(producers.SilvaProducer):
    """Export a version of an AgendaItem object to XML.
    """
    grok.adapts(interfaces.IAgendaItemVersion, Interface)

    def sax(self):
        """sax"""
        self.startElement(
            'content',
            {'version_id': self.context.id,
             'subjects': ','.join(self.context.get_subjects()),
             'target_audiences': ','.join(self.context.get_target_audiences()),
             'display_datetime': iso_datetime(
                self.context.get_display_datetime())})
        self.sax_metadata()
        for occurrence in self.context.get_occurrences():
            self.startElementNS(
                NS_NEWS_URI, 'occurrence',
                {'start_datetime': iso_datetime(
                        occurrence.get_start_datetime()),
                 'end_datetime': iso_datetime(
                        occurrence.get_end_datetime()),
                 'location': occurrence.get_location(),
                 'recurrence': occurrence.get_recurrence() or '',
                 'all_day': str(occurrence.is_all_day()),
                 'timezone_name': occurrence.get_timezone_name()})
            self.endElementNS(NS_NEWS_URI, 'occurrence')
        self.sax_content()
        self.endElement('content')

    def sax_content(self):
        self.startElementNS(NS_NEWS_URI, 'body')
        TextProducerProxy(self.context, self.context.body).sax(self)
        self.endElementNS(NS_NEWS_URI, 'body')
