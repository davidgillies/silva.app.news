# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.silvaxml.xmlexport import theXMLExporter, VersionedContentProducer, SilvaBaseProducer
from Products.SilvaDocument.silvaxml.xmlexport import DocumentVersionProducer

NS_SILVANEWS = 'http://infrae.com/ns/silva-news-network'

def initializeXMLExportRegistry():
    from Products.SilvaNews.NewsViewer import NewsViewer
    #from Products.SilvaNews.PlainArticle import PlainArticle, PlainArticleVersion
    #from Products.SilvaNews.PlainAgendaItem import PlainAgendaItem, PlainAgendaItemVersion
    #from Products.SilvaNews.NewsItem import NewsItemVersion
    
    exporter = theXMLExporter
    exporter.registerNamespace('silvanews', NS_SILVANEWS)
    exporter.registerProducer(NewsViewer, NewsViewerProducer)
    #exporter.registerProducer(PlainArticle, PlainArticleProducer)
    #exporter.registerProducer(PlainArticleVersion, PlainArticleVersionProducer)
    #exporter.registerProducer(PlainAgendaItem, PlainArticleProducer)
    #exporter.registerProducer(PlainAgendaItemVersion, PlainAgendaItemVersionProducer)

class NewsViewerProducer(SilvaBaseProducer):
     """Export a NewsViewer object to XML."""
     def sax(self):
         self.startElementNS(NS_SILVANEWS,
                           'newsviewer',
                           {'id': self.context.id,
                            'number_to_show': str(self.context.number_to_show()),
                            'number_to_show_archive': str(self.context.number_to_show_archive()),
                            'number_is_days': str(self.context.number_is_days()),
                            'filters': str(self.context.filters())})
         self.metadata()
         self.endElementNS(NS_SILVANEWS,'newsviewer')

#         self.startElement('auto_toc', {'id': self.context.id,
#                                        'depth': str(self.context.toc_depth()),
#                                        'types': ','.join(self.context.get_local_types()),
#                                        'sort_order': self.context.sort_order(),
#                                        'show_icon': str(self.context.show_icon()),
#                                        'display_desc_flag': str(self.context.display_desc_flag())})
#         self.metadata()
#         self.endElement('auto_toc')


# class PlainArticleProducer(VersionedContentProducer):
#     """Export a PlainArticle object to XML.
#     """
#     def sax(self):
#         """sax"""
#         self.startElement('newsitem', {'id': self.context.id})
#         self.workflow()
#         self.versions()
#         self.endElement('newsitem')

# class PlainArticleVersionProducer(DocumentVersionProducer):
#     """Export a version of a PlainArticle object to XML.
#     """
#     def sax(self):
#         """sax"""
#         self.startElement('sta')
#         for subject in self.context.subjects():
#             self.startElement('subject')
#             self.handler.characters(subject)
#             self.endElement('subject')
#         for audience in self.context.target_audiences():
#             self.startElement('target_audience')
#             self.handler.characters(audience)
#             self.endElement('target_audience')
#         self.endElement('sta')
#         self.startElement('content', {'version_id': self.context.id})
#         self.metadata()
#         # needed to add _content to the line below to access the parsedXML - jon
#         node = self.context.content._content.documentElement.getDOMObj()
#         self.sax_node(node)
#         self.endElement('content')

# class PlainAgendaItemVersionProducer(DocumentVersionProducer):
#     """Export a version of a PlainAgendaItem object to XML.
#     """
#     def sax(self):
#         """sax"""
#         self.startElement('sta')
#         for subject in self.context.subjects():
#             self.startElement('subject')
#             self.handler.characters(subject)
#             self.endElement('subject')
#         for audience in self.context.target_audiences():
#             self.startElement('target_audience')
#             self.handler.characters(audience)
#             self.endElement('target_audience')
#         #additional attributes for agendaItems
#         self.startElement('start_datetime')
#         self.handler.characters(self.context.start_datetime().HTML4())
#         self.endElement('start_datetime')
#         self.startElement('end_datetime')
#         self.handler.characters(self.context.end_datetime().HTML4())
#         self.endElement('end_datetime')
#         self.startElement('location')
#         self.handler.characters(self.context.location())
#         self.endElement('location')
#         self.endElement('sta')
#         self.startElement('content', {'version_id': self.context.id})
#         self.metadata()
#         # needed to add _content to the line below to access the parsedXML - jon
#         node = self.context.content._content.documentElement.getDOMObj()
#         self.sax_node(node)
#         self.endElement('content')
