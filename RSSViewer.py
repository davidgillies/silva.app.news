# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $

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

def get_text_from_children(node):
    """Returns all textnode values concatenated"""
    retval = ''
    for n in node.childNodes:
        if n.nodeType == 3:
            retval += n.nodeValue.encode('cp1252', 'replace')
    return retval

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
                self.get_title_html = get_text_from_children(node)
            elif node.nodeName == u'link':
                self.url = get_text_from_children(node)
            elif node.nodeName == u'description':
                self.lead = get_text_from_children(node)

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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items')
    def get_items(self):
        """Gets the items from the RSS feed
        """
        # I declare properties here, since they need to be flushed anyway
        self._rss_title = ''
        self._rss_link = ''
        self._rss_description = ''
        self._rss_copyright = ''
        self._rss_publication_date = ''
        self._rss_image_title = ''
        self._rss_image_url = ''
        self._rss_image_link = ''
        self._rss_textinput_title = ''
        self._rss_textinput_description = ''
        self._rss_textinput_name = ''
        self._rss_textinput_link = ''
        results = []
        feedxml = urlopen(self._rss_feed).read()
        dom = parseString(feedxml)
        rssnode = dom.childNodes[0]
        if rssnode.nodeName != u'rss' and rssnode.nodeName != u'rdf:RDF':
            raise Exception, 'RSS format with main node %s not supported!' % rssnode.nodeName.encode('cp1252')
        elif (rssnode.nodeName == u'rss' and 'version' in rssnode._attrs.keys() and rssnode._attrs['version'].nodeValue == u'0.91'):
            # RSS version 0.91
            for node in rssnode.childNodes:
                if node.nodeName == u'channel':
                    for n in node.childNodes:
                        if n.nodeName == u'title':
                            self._rss_title = get_text_from_children(n)
                        elif n.nodeName == u'link':
                            self._rss_link = get_text_from_children(n)
                        elif n.nodeName == u'description':
                            self._rss_description = get_text_from_children(n)
                        elif n.nodeName == u'copyright':
                            self._rss_copyright = get_text_from_children(n)
                        elif n.nodeName == u'pubDate':
                            self._rss_publication_date = get_text_from_children(n)
                        elif n.nodeName == u'image':
                            for inode in n.childNodes:
                                if inode.nodeName == u'title':
                                    self._rss_image_title = get_text_from_children(inode)
                                elif inode.nodeName == u'link':
                                    self._rss_image_link = get_text_from_children(inode)
                                elif inode.nodeName == u'url':
                                    self._rss_image_url = get_text_from_children(inode)
                        elif n.nodeName == u'textinput':
                            for inode in n.childNodes:
                                if inode.nodeName == u'title':
                                    self._rss_textinput_title = get_text_from_children(inode)
                                if inode.nodeName == u'description':
                                    self._rss_textinput_description = get_text_from_children(inode)
                                if inode.nodeName == u'name':
                                    self._rss_textinput_name = get_text_from_children(inode)
                                if inode.nodeName == u'link':
                                    self._rss_textinput_link = get_text_from_children(inode)
                        elif n.nodeName == u'item':
                            results.append(RSSBrain(n))
        elif rssnode.nodeName == u'rdf:RDF' and 'xmlns' in rssnode._attrs.keys() and (rssnode._attrs['xmlns'].nodeValue.startswith(u'http://purl.org/rss/1.0') or rssnode._attrs['xmlns'].nodeValue.startswith(u'http://my.netscape.com/rdf/simple/0.9/')):
            # RSS version 1.0
            for node in rssnode.childNodes:
                if node.nodeName == u'channel':
                    for n in node.childNodes:
                        if n.nodeName == u'title':
                            self._rss_title = get_text_from_children(n)
                        elif n.nodeName == u'link':
                            self._rss_link = get_text_from_children(n)
                        elif n.nodeName == u'description':
                            self._rss_description = get_text_from_children(n)
                        elif n.nodeName == u'dc:rights':
                            self._rss_copyright = get_text_from_children(n)
                        elif n.nodeName == u'dc:date':
                            self._rss_publication_date = get_text_from_children(n)
                elif node.nodeName == u'image':
                    for inode in node.childNodes:
                        if inode.nodeName == u'title':
                            self._rss_image_title = get_text_from_children(inode)
                        elif inode.nodeName == u'link':
                            self._rss_image_link = get_text_from_children(inode)
                        elif inode.nodeName == u'url':
                            self._rss_image_url = get_text_from_children(inode)
                elif node.nodeName == u'textinput':
                    for inode in node.childNodes:
                        if inode.nodeName == u'title':
                            self._rss_textinput_title = get_text_from_children(inode)
                        if inode.nodeName == u'description':
                            self._rss_textinput_description = get_text_from_children(inode)
                        if inode.nodeName == u'name':
                            self._rss_textinput_name = get_text_from_children(inode)
                        if inode.nodeName == u'link':
                            self._rss_textinput_link = get_text_from_children(inode)
                elif node.nodeName == u'item':
                    results.append(RSSBrain(node))
        else:
            raise Exception, 'RSS version not supported!'

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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_link')
    def rss_link(self):
        """Returns the link to the URL of the RSS feed's site"""
        return self._rss_link

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_description')
    def rss_description(self):
        """Returns the description of the RSS feed"""
        return self._rss_description

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_copyright')
    def rss_copyright(self):
        """Returns the copyright notice of the RSS feed"""
        return self._rss_copyright

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_publication_date')
    def rss_publication_date(self):
        """Returns the publication date of the RSS feed"""
        return self._rss_publication_date

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_image_url')
    def rss_image_url(self):
        """Returns the URL of the image (if any)"""
        return self._rss_image_url

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_image_title')
    def rss_image_title(self):
        """Returns the title of the image (if any)"""
        return self._rss_image_title

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_image_link')
    def rss_image_link(self):
        """Returns the URL of the image (if any)"""
        return self._rss_image_link

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_textinput_title')
    def rss_textinput_title(self):
        """Returns the title of the textinput part"""
        return self._rss_textinput_title

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_textinput_description')
    def rss_textinput_description(self):
        """Returns the description of the textinput part"""
        return self._rss_textinput_description

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_textinput_name')
    def rss_textinput_name(self):
        """Returns the name of the textinput part"""
        return self._rss_textinput_name

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_textinput_link')
    def rss_textinput_link(self):
        """Returns the link of the textinput part"""
        return self._rss_textinput_link

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
