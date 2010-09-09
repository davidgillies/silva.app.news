# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core.interfaces import IPublication
from five import grok
from zope.interface import Interface

from Products.SilvaNews import interfaces
from Products.SilvaDocument.silvaxml.xmlexport import DocumentVersionProducer
from Products.Silva.silvaxml.xmlexport import (
    theXMLExporter, VersionedContentProducer, SilvaBaseProducer)


NS_SILVA_NEWS = 'http://infrae.com/namespace/silva-news-network'
theXMLExporter.registerNamespace('silvanews', NS_SILVA_NEWS)


class NewsPublicationProducer(SilvaBaseProducer):
    """Export a News Publication object to XML.
    """
    grok.adapts(interfaces.INewsPublication, Interface)

    def sax(self):
        self.startElementNS(NS_SILVA_NEWS,
                            'newspublication', {'id': self.context.id})
        self.metadata()
        self.startElement('content')
        default = self.context.get_default()
        if default is not None:
            self.startElement('default')
            self.subsax(default)
            self.endElement('default')
        for object in self.context.get_ordered_publishables():
            if (IPublication.providedBy(object) and
                    not self.getSettings().withSubPublications()):
                continue
            self.subsax(object)
        for object in self.context.get_assets():
            self.subsax(object)
        if self.getSettings().otherContent():
            for object in self.context.get_other_content():
                self.subsax(object)
        self.endElement('content')
        self.endElementNS(NS_SILVA_NEWS,'newspublication')


class RSSAggregatorProducer(SilvaBaseProducer):
     """Export a RSSAggregator object to XML.
     """
     grok.adapts(interfaces.IAggregator, Interface)

     def sax(self):
         self.startElementNS(
             NS_SILVA_NEWS,
             'rssaggregator',
             {'id': self.context.id,
              'feed_urls': ','.join(self.context.get_feeds())
              })
         self.metadata()
         self.endElementNS(NS_SILVA_NEWS,'rssaggregator')


class CategoryFilterProducer(SilvaBaseProducer):
     """Export a CategoryFilter object to XML."""
     grok.adapts(interfaces.ICategoryFilter, Interface)

     def sax(self):
         self.startElementNS(
             NS_SILVA_NEWS,
             'categoryfilter',
             {'id': self.context.id,
              'target_audiences': ','.join(self.context.target_audiences()),
              'subjects': ','.join(self.context.subjects()),
              })
         self.metadata()
         self.endElementNS(NS_SILVA_NEWS,'categoryfilter')


class NewsFilterProducer(SilvaBaseProducer):
     """Export a NewsFilter object to XML.
     """
     grok.adapts(interfaces.INewsFilter, Interface)

     def sax(self):
         self.startElementNS(
             NS_SILVA_NEWS,
             'newsfilter',
             {'id': self.context.id,
              'target_audiences': ','.join(self.context.target_audiences()),
              'subjects': ','.join(self.context.subjects()),
              'show_agenda_items': str(self.context.show_agenda_items()),
              'keep_to_path': str(self.context.keep_to_path()),
              'excluded_items': ','.join(self.context.excluded_items()),
              'sources': ','.join(self.context.sources())})
         self.metadata()
         self.endElementNS(NS_SILVA_NEWS,'newsfilter')


class AgendaFilterProducer(SilvaBaseProducer):
     """Export a AgendaFilter object to XML.
     """
     grok.adapts(interfaces.IAgendaFilter, Interface)

     def sax(self):
         self.startElementNS(
             NS_SILVA_NEWS,
             'agendafilter',
             {'id': self.context.id,
              'target_audiences': ','.join(self.context.target_audiences()),
              'subjects': ','.join(self.context.subjects()),
              'keep_to_path': str(self.context.keep_to_path()),
              'excluded_items': ','.join(self.context.excluded_items()),
              'sources': ','.join(self.context.sources())})
         self.metadata()
         self.endElementNS(NS_SILVA_NEWS,'agendafilter')


class NewsViewerProducer(SilvaBaseProducer):
     """Export a NewsViewer object to XML.
     """
     grok.adapts(interfaces.INewsViewer, Interface)

     def sax(self):
         self.startElementNS(
             NS_SILVA_NEWS,
             'newsviewer',
             {'id': self.context.id,
              'number_to_show': str(self.context.number_to_show()),
              'number_to_show_archive': str(self.context.number_to_show_archive()),
              'number_is_days': str(self.context.number_is_days()),
              'filters': ','.join(self.context.filters())})
         self.metadata()
         self.endElementNS(NS_SILVA_NEWS,'newsviewer')


class AgendaViewerProducer(SilvaBaseProducer):
     """Export a AgendaViewer object to XML."""
     grok.adapts(interfaces.IAgendaViewer)

     def sax(self):
         self.startElementNS(
             NS_SILVA_NEWS,
             'agendaviewer',
             {'id': self.context.id,
              'days_to_show': str(self.context.days_to_show()),
              'number_to_show_archive': str(self.context.number_to_show_archive()),
              'filters': ','.join(self.context.filters())})
         self.metadata()
         self.endElementNS(NS_SILVA_NEWS,'agendaviewer')


class PlainArticleProducer(VersionedContentProducer):
    """Export a PlainArticle object to XML.
    """
    grok.adapts(interfaces.INewsItem, Interface)

    def sax(self):
        """sax"""
        self.startElementNS(NS_SILVA_NEWS,
                            'plainarticle',
                            {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElementNS(NS_SILVA_NEWS,'plainarticle')


class PlainArticleVersionProducer(DocumentVersionProducer):
    """Export a version of a PlainArticle object to XML.
    """
    grok.adapts(interfaces.INewsItemVersion)

    def sax(self):
        """sax"""
        self.startElement(
            'content',
            {'version_id': self.context.id,
             'subjects': ','.join(self.context.subjects()),
             'target_audiences': ','.join(self.context.target_audiences())})
        self.metadata()
        node = self.context.content.documentElement.getDOMObj()
        self.sax_node(node)
        self.endElement('content')


class PlainAgendaItemProducer(VersionedContentProducer):
    """Export an AgendaItem object to XML.
    """
    grok.adapts(interfaces.IAgendaItem)

    def sax(self):
        """sax"""
        self.startElementNS(NS_SILVA_NEWS,
                            'agendaitem',
                            {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElementNS(NS_SILVA_NEWS,'agendaitem')


class PlainAgendaItemVersionProducer(DocumentVersionProducer):
    """Export a version of an AgendaItem object to XML.
    """
    grok.adapts(interfaces.IAgendaItemVersion)

    def sax(self):
        """sax"""
        edt = self.context.end_datetime()
        if edt:
            edt = edt.isoformat()
        self.startElement(
            'content',
            {'version_id': self.context.id,
             'subjects': ','.join(self.context.get_subjects()),
             'target_audiences': ','.join(self.context.get_target_audiences()),
             'start_datetime':self.context.get_start_datetime().isoformat(),
             'end_datetime':edt,
             'location':self.context.get_location()})
        self.metadata()
        node = self.context.content.documentElement.getDOMObj()
        self.sax_node(node)
        self.endElement('content')
