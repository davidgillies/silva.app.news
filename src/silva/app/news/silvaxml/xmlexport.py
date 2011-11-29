# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.interface import Interface

# reference management (will move somewhere else)
from zope.traversing.browser import absoluteURL
from silva.core.references.reference import ReferenceSet
from silva.app.news import interfaces
from silva.app.news.datetimeutils import utc_datetime
from silva.app.news.silvaxml import NS_NEWS_URI
from silva.core.references.utils import is_inside_container
from silva.core.references.utils import relative_path
from silva.core.references.utils import canonical_path
from silva.core.editor.transform.silvaxml.xmlexport import TextProducerProxy

from Products.Silva.silvaxml import xmlexport
from Products.Silva.silvaxml.xmlexport import ExternalReferenceError


xmlexport.registerNamespace('silva-app-news', NS_NEWS_URI)

def iso_datetime(dt):
    if dt:
        string = utc_datetime(dt).replace(microsecond=0).isoformat()
        if string.endswith('+00:00'):
            string = string[:-6] + 'Z'
        return string
    return ''


class ReferenceSupportExporter(object):

    def reference_set_paths(self, name):
        ref_set = ReferenceSet(self.context, name)
        settings = self.getSettings()
        info = self.getInfo()
        root = info.root
        for reference in ref_set.get_references():
            if not settings.externalRendering():
                if not reference.target_id:
                    # The reference is broken. Return an empty path.
                    yield ""
                if not reference.is_target_inside_container(root):
                    raise ExternalReferenceError(
                        self.context, reference.target, root)
                # Add root path id as it is always mentioned in exports
                path = [root.getId()] + reference.relative_path_to(root)
                yield canonical_path('/'.join(path))
            else:
                # Return url to the target
                yield absoluteURL(reference.target, info.request)


class NewsPublicationProducer(xmlexport.SilvaContainerProducer):
    """Export a News Publication object to XML.
    """
    grok.adapts(interfaces.INewsPublication, Interface)

    def sax(self):
        self.startElementNS(
            NS_NEWS_URI, 'news_publication', {'id': self.context.id})
        self.metadata()
        self.contents()
        self.endElementNS(NS_NEWS_URI,'news_publication')


class RSSAggregatorProducer(xmlexport.SilvaProducer):
     """Export a RSSAggregator object to XML.
     """
     grok.adapts(interfaces.IRSSAggregator, Interface)

     def sax(self):
         self.startElementNS(
             NS_NEWS_URI, 'rss_aggregator', {'id': self.context.id})
         self.metadata()
         for feed in self.context.get_feeds():
             self.startElementNS(NS_NEWS_URI, 'url')
             self.handler.characters(feed)
             self.endElementNS(NS_NEWS_URI, 'url')
         self.endElementNS(NS_NEWS_URI, 'rss_aggregator')


class NewsFilterProducer(xmlexport.SilvaProducer, ReferenceSupportExporter):
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
        self.metadata()
        self.startElement('content')
        self.sources()
        self.excludes()
        self.endElement('content')
        self.endElementNS(NS_NEWS_URI,'news_filter')

    def sources(self):
        self.startElementNS(NS_NEWS_URI, "sources")
        for source_path in self.reference_set_paths("sources"):
            if source_path:
                self.startElementNS(
                    NS_NEWS_URI, 'source', {'target': source_path})
                self.endElementNS(NS_NEWS_URI, 'source')
        self.endElementNS(NS_NEWS_URI, "sources")

    def excludes(self):
        self.startElementNS(NS_NEWS_URI, "excludes")
        root = self.getInfo().root
        for item in self.context.get_excluded_items():
            if is_inside_container(root, item):
                path = [root.getId()] + relative_path(
                    root.getPhysicalPath(), item.getPhysicalPath())
                path = canonical_path('/'.join(path))
                self.startElementNS(
                    NS_NEWS_URI, 'exclude', {'target': path})
                self.endElementNS(NS_NEWS_URI, 'exclude')
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
        self.metadata()
        self.startElement('content')
        self.sources()
        self.excludes()
        self.endElement('content')
        self.endElementNS(NS_NEWS_URI,'agenda_filter')


class NewsViewerProducer(xmlexport.SilvaProducer, ReferenceSupportExporter):
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
             'number_is_days': str(self.context.get_number_is_days())})
        self.metadata()
        self.startElement('content')
        self.filters()
        self.endElement('content')
        self.endElementNS(NS_NEWS_URI,'news_viewer')

    def filters(self):
        self.startElementNS(NS_NEWS_URI, "filters")
        for filter_path in self.reference_set_paths("filters"):
            if filter_path:
                self.startElementNS(
                    NS_NEWS_URI, 'filter', {'target': filter_path})
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
             'days_to_show': str(self.context.days_to_show()),
             'number_to_show_archive': str(
                    self.context.number_to_show_archive())})
        self.metadata()
        self.startElement('content')
        self.filters()
        self.endElement('content')
        self.endElementNS(NS_NEWS_URI,'agenda_viewer')


class NewsItemProducer(xmlexport.SilvaVersionedContentProducer):
    """Export a NewsItem object to XML.
    """
    grok.adapts(interfaces.INewsItem, Interface)

    def sax(self):
        """sax"""
        self.startElementNS(
            NS_NEWS_URI, 'news_item', {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElementNS(NS_NEWS_URI,'news_item')


class NewsItemVersionProducer(xmlexport.SilvaProducer):
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
        self.metadata()
        self.startElementNS(NS_NEWS_URI, 'body')
        TextProducerProxy(self.context, self.context.body).sax(self)
        self.endElementNS(NS_NEWS_URI, 'body')
        self.endElement('content')


class AgendaItemProducer(xmlexport.SilvaVersionedContentProducer):
    """Export an AgendaItem object to XML.
    """
    grok.adapts(interfaces.IAgendaItem, Interface)

    def sax(self):
        """sax"""
        self.startElementNS(
            NS_NEWS_URI, 'agenda_item', {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElementNS(NS_NEWS_URI,'agenda_item')


class AgendaItemVersionProducer(xmlexport.SilvaProducer):
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
        self.metadata()
        self.startElementNS(NS_NEWS_URI, 'body')
        TextProducerProxy(self.context, self.context.body).sax(self)
        self.endElementNS(NS_NEWS_URI, 'body')
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
        self.endElement('content')


