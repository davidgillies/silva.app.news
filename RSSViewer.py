# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $

from urllib import urlopen
from xml.dom.minidom import parseString

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS import Folder

from Products.Silva.IContent import IContent
from Products.Silva.TocSupport import TocSupport
from Products.Silva import SilvaPermissions
from Products.Silva.Content import Content
from Products.Silva.Document import Document
from Products.Silva.helpers import add_and_edit

from Products.SilvaNews.NewsViewer import NewsViewer

class RSSBrain:
    """Wrapper around RSS items so they can be used in the same code that uses ZCatalog NewsItem Brains"""

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    def __init__(self, itemnode):
        self.subheader = ''
        self.lead = ''
        self.start_datetime = None
        self.get_title_html = ''
        self.url = ''

        for node in itemnode.childNodes:
            if node.nodeName == u'title':
                for textNode in node.childNodes:
                    if textNode.nodeType == 3:
                        self.get_title_html += textNode.nodeValue.encode('cp1252', 'replace')
            elif node.nodeName == u'link':
                for textNode in node.childNodes:
                    if textNode.nodeType == 3:
                        self.url += textNode.nodeValue.encode('cp1252', 'replace')
            elif node.nodeName == u'description':
                for textNode in node.childNodes:
                    if textNode.nodeType == 3:
                        self.lead += textNode.nodeValue.encode('cp1252', 'replace')

    def getURL(self):
        return self.url

InitializeClass(RSSBrain)

class RSSViewer(NewsViewer):
    """Silva RSSViewer, supports RSS versions 0.91 and 1.0
    """

    security = ClassSecurityInfo()

    __implements__ = IContent

    meta_type = 'Silva News RSSViewer'

    def __init__(self, id, title):
        RSSViewer.inheritedAttribute('__init__')(self, id, title)
        self._rss_feed = ''
        self._rss_title = ''

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items')
    def get_items(self):
        """Gets the items from the RSS feed
        """
        results = []
        feedxml = urlopen(self._rss_feed).read()
        dom = parseString(feedxml)
        rssnode = dom.childNodes[0]
        if rssnode.nodeName != u'rss' and rssnode.nodeName != u'rdf:RDF':
            raise Exception, 'RSS format with main node %s not supported!' % rssnode.nodeName.encode('cp1252')
        elif rssnode.nodeName == u'rss':
            # RSS version 0.91
            for node in rssnode.childNodes:
                if node.nodeName == u'channel':
                    for n in node.childNodes:
                        if n.nodeName == u'title':
                            self._rss_title = ''
                            for t in n.childNodes:
                                if t.nodeType == 3:
                                    self._rss_title += t.nodeValue
                        elif n.nodeName == u'item':
                            results.append(RSSBrain(n))
        elif rssnode.nodeName == u'rdf:RDF':
            for node in rssnode.childNodes:
                if node.nodeName == u'channel':
                    print "Found channel node"
                    for n in node.childNodes:
                        if n.nodeName == u'title':
                            print "Found title node"
                            self._rss_title = ''
                            for t in n.childNodes:
                                if t.nodeType == 3:
                                    self._rss_title += t.nodeValue
                elif node.nodeName == u'item':
                    results.append(RSSBrain(node))
        return results

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_rss_feed')
    def set_rss_feed(self, url):
        """Sets the URL for the RSS feed to use"""
        self._rss_feed = url

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_feed')
    def rss_feed(self):
        """Returns the URL of the RSS feed"""
        return self._rss_feed

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_title')
    def rss_title(self):
        """Returns the title of the RSS feed"""
        return self._rss_title

InitializeClass(RSSViewer)

manage_addRSSViewerForm = PageTemplateFile(
    "www/rssViewerAdd", globals(),
    __name__='manage_addRSSViewerForm')

def manage_addRSSViewer(self, id, title, REQUEST=None):
    """Add a News RSSViewer."""
    if not self.is_id_valid(id):
        return
    object = RSSViewer(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
