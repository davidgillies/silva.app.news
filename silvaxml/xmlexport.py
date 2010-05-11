# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.silvaxml.xmlexport import theXMLExporter, VersionedContentProducer, SilvaBaseProducer
from silva.core.interfaces import IPublication
from Products.SilvaDocument.silvaxml.xmlexport import DocumentVersionProducer

NS_SILVANEWS = 'http://infrae.com/namespace/silva-news-network'

def initializeXMLExportRegistry():
    from Products.SilvaNews.viewers.NewsViewer import NewsViewer
    from Products.SilvaNews.viewers.AgendaViewer import AgendaViewer
    from Products.SilvaNews.filters.NewsFilter import NewsFilter
    from Products.SilvaNews.filters.AgendaFilter import AgendaFilter
    from Products.SilvaNews.filters.CategoryFilter import CategoryFilter
    from Products.SilvaNews.RSSAggregator import RSSAggregator
    from Products.SilvaNews.NewsPublication import NewsPublication
    from Products.SilvaNews.PlainArticle import PlainArticle, PlainArticleVersion
    from Products.SilvaNews.PlainAgendaItem import PlainAgendaItem, PlainAgendaItemVersion

    exporter = theXMLExporter
    exporter.registerNamespace('silvanews', NS_SILVANEWS)
    exporter.registerProducer(NewsViewer, NewsViewerProducer)
    exporter.registerProducer(AgendaViewer, AgendaViewerProducer)
    exporter.registerProducer(NewsFilter, NewsFilterProducer)
    exporter.registerProducer(AgendaFilter, AgendaFilterProducer)
    exporter.registerProducer(CategoryFilter, CategoryFilterProducer)
    exporter.registerProducer(RSSAggregator, RSSAggregatorProducer)
    exporter.registerProducer(NewsPublication, NewsPublicationProducer)
    exporter.registerProducer(PlainArticle, PlainArticleProducer)
    exporter.registerProducer(PlainArticleVersion, PlainArticleVersionProducer)
    exporter.registerProducer(PlainAgendaItem, PlainAgendaItemProducer)
    exporter.registerProducer(PlainAgendaItemVersion, PlainAgendaItemVersionProducer)


class NewsPublicationProducer(SilvaBaseProducer):
    """Export a News Publication object to XML.
    """
    def sax(self):
        self.startElementNS(NS_SILVANEWS,
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
        self.endElementNS(NS_SILVANEWS,'newspublication')


class RSSAggregatorProducer(SilvaBaseProducer):
     """Export a RSSAggregator object to XML.
     """

     def sax(self):
         self.startElementNS(
             NS_SILVANEWS,
             'rssaggregator',
             {'id': self.context.id,
              'feed_urls': ','.join(self.context.get_feeds())
              })
         self.metadata()
         self.endElementNS(NS_SILVANEWS,'rssaggregator')


class CategoryFilterProducer(SilvaBaseProducer):
     """Export a CategoryFilter object to XML."""
     def sax(self):
         self.startElementNS(
             NS_SILVANEWS,
             'categoryfilter',
             {'id': self.context.id,
              'target_audiences': ','.join(self.context.target_audiences()),
              'subjects': ','.join(self.context.subjects()),
              })
         self.metadata()
         self.endElementNS(NS_SILVANEWS,'categoryfilter')


class NewsFilterProducer(SilvaBaseProducer):
     """Export a NewsFilter object to XML.
     """

     def sax(self):
         self.startElementNS(
             NS_SILVANEWS,
             'newsfilter',
             {'id': self.context.id,
              'target_audiences': ','.join(self.context.target_audiences()),
              'subjects': ','.join(self.context.subjects()),
              'show_agenda_items': str(self.context.show_agenda_items()),
              'keep_to_path': str(self.context.keep_to_path()),
              'excluded_items': ','.join(self.context.excluded_items()),
              'sources': ','.join(self.context.sources())})
         self.metadata()
         self.endElementNS(NS_SILVANEWS,'newsfilter')


class AgendaFilterProducer(SilvaBaseProducer):
     """Export a AgendaFilter object to XML.
     """

     def sax(self):
         self.startElementNS(
             NS_SILVANEWS,
             'agendafilter',
             {'id': self.context.id,
              'target_audiences': ','.join(self.context.target_audiences()),
              'subjects': ','.join(self.context.subjects()),
              'keep_to_path': str(self.context.keep_to_path()),
              'excluded_items': ','.join(self.context.excluded_items()),
              'sources': ','.join(self.context.sources())})
         self.metadata()
         self.endElementNS(NS_SILVANEWS,'agendafilter')


class NewsViewerProducer(SilvaBaseProducer):
     """Export a NewsViewer object to XML.
     """

     def sax(self):
         self.startElementNS(
             NS_SILVANEWS,
             'newsviewer',
             {'id': self.context.id,
              'number_to_show': str(self.context.number_to_show()),
              'number_to_show_archive': str(self.context.number_to_show_archive()),
              'number_is_days': str(self.context.number_is_days()),
              'filters': ','.join(self.context.filters())})
         self.metadata()
         self.endElementNS(NS_SILVANEWS,'newsviewer')


class AgendaViewerProducer(SilvaBaseProducer):
     """Export a AgendaViewer object to XML."""
     def sax(self):
         self.startElementNS(NS_SILVANEWS,
                           'agendaviewer',
                           {'id': self.context.id,
                            'days_to_show': str(self.context.days_to_show()),
                            'number_to_show_archive': str(self.context.number_to_show_archive()),
                            'filters': ','.join(self.context.filters())})
         self.metadata()
         self.endElementNS(NS_SILVANEWS,'agendaviewer')


class PlainArticleProducer(VersionedContentProducer):
    """Export a PlainArticle object to XML.
    """
    def sax(self):
        """sax"""
        self.startElementNS(NS_SILVANEWS,
                            'plainarticle',
                            {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElementNS(NS_SILVANEWS,'plainarticle')


class PlainArticleVersionProducer(DocumentVersionProducer):
    """Export a version of a PlainArticle object to XML.
    """

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

    def sax(self):
        """sax"""
        self.startElementNS(NS_SILVANEWS,
                            'agendaitem',
                            {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElementNS(NS_SILVANEWS,'agendaitem')


class PlainAgendaItemVersionProducer(DocumentVersionProducer):
    """Export a version of an AgendaItem object to XML.
    """

    def sax(self):
        """sax"""
        edt = self.context.end_datetime()
        if edt:
            edt = edt.isoformat()
        self.startElement(
            'content',
            {'version_id': self.context.id,
             'subjects': ','.join(self.context.subjects()),
             'target_audiences': ','.join(self.context.target_audiences()),
             'start_datetime':self.context.start_datetime().isoformat(),
             'end_datetime':edt,
             'location':self.context.location()})
        self.metadata()
        node = self.context.content.documentElement.getDOMObj()
        self.sax_node(node)
        self.endElement('content')
