# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.6 $

from urllib import urlopen
import time
from threading import Thread
from xml.dom.minidom import parseString

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS import Folder
from DateTime import DateTime

from Products.Silva.IContent import IContent
from Products.Silva.TocSupport import TocSupport
from Products.Silva import SilvaPermissions
from Products.Silva.Content import Content
from Products.Silva.Document import Document
from Products.Silva.helpers import add_and_edit

from Products.SilvaNews.NewsViewer import NewsViewer

class TimeoutWrapper:
    """Used to run a certain method with a timeout.

    Usage:

    t = TimeoutWrapper(<method>, <args>, <kwargs>)
    success = t.run_with_timeout(<timeout>)
    if success:
        retval = t.return_value()
    else:
        raise Exception, 'Operation timed out'

    When calling the 'run_with_timeout' method, <method> is called with arguments <args> and keyword arguments <kwargs>.
    If the method succeeds within the requested time, 1 is returned, and the result of the call can be retrieved using 
    the 'return_value' method. If this process takes longer then <timeout> (seconds), 0 is returned by the 
    'run_with_timeout' method (and 'return_value' returns None).
    """
    
    def __init__(self, handler, args=(), kwargs={}):
        """Initializes the object.
        
        Arguments are:
        
        - handler: a reference to the method to be called
        - args: a list of non-keyword arguments that should be passed to the method
        - kwargs: a dict of keyword arguments that should be passed to the method
        """
        self._handler = handler
        self._args = args
        self._kwargs = kwargs
        self._success = 0
        self._retval = None

    def run_with_timeout(self, timeout):
        """Class the method

        Arguments are:
        
        - timeout: an integer (or float) specifying the timeout in seconds
        """
        thread = Thread(target=self._run_thread)
        thread.start()
        thread.join(timeout)
        del thread
        return self._success

    def return_value(self):
        """Returns the return value of the method (if any)

        No arguments required.
        """
        return self._retval

    def _run_thread(self):
        """Internal method that actually calls the method.

        Will set self._retval and self._success if successful.
        """
        self._retval = self._handler(*self._args, **self._kwargs)
        self._success = 1
        
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
        self._rss_last_modified = ''
        self._last_rss_feed = ''
        self._last_result = []
        self._caching_period = 30 # in seconds, 0 means don't cache
        self._last_request_time = time.time()
        self._rss_timeout = 30 # in seconds

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items')
    def get_items(self):
        """Gets the items from the RSS server and serves them
        
        Will try to cache in 2 different ways:
        
        1. Using a time setting - the manager of the RSS viewer can set a minimal amount of time the content should be cached,
                                            before this time is due the viewer will use cached data (if any), regardless of whether there
                                            is new data available on the server
        2. Using HTTP caching headers - if the server sends out an HTTP Last-Modified header, this is checked against the last 
                                            received Last-Modified header, and if those two are the same then the viewer will use
                                            cached data (if any). FIXME: It would be nice to just send a HEAD request instead of the full monty...
        """
        result = []
        # check if we want to use the cached version because of time settings, if so:
        if (self._last_result and 
            self._rss_feed == self._last_rss_feed and 
            self._caching_period != 0 and 
            (time.time() - self._last_request_time) < self._caching_period):
            print "Using cached version because of timeout settings"
            # use the cached version
            result = self._last_result
            # update the timestamps
            self._last_request_time = time.time()
        # if we're not gonna use the cached version because of caching_period settings:
        else:
            # download the data (with a timeout)
            t = TimeoutWrapper(urlopen, (self._rss_feed,))
            success = t.run_with_timeout(self._rss_timeout)
            # if successful:
            if success:
                # get the headers and data
                ret = t.return_value()
                info = ret.info()
                data = ret.read()
                # check if there is a new version (using Last-Modified), if there isn't:
                lm = info.getheader('Last-Modified', None)
                if lm and lm == self._rss_last_modified:
                    print "Using cached version because of Last-Modified header"
                    # use the cached version
                    result = self._last_result
                    # update the timestamps
                    self._last_request_time = time.time()
                # if there is a new version or the Last-Modified header is not set:
                else:
                    print "Headers:"
                    print info.headers
                    print "Retrieving new data"
                    # parse the new version
                    result = self._parse_rss_stream(data)
                    # update the caches
                    self._last_result = result
                    self._last_rss_feed = self._rss_feed
                    # update the timestamps
                    self._last_request_time = time.time()
            # else if not successful:
            else:
                print "Using cached version because of timeout"
                # use the cached version
                result = self._last_result
                # update the timestamps
                self._last_request_time = time.time()

        self._p_changed = 1
        # return
        return result

    def _parse_rss_stream(self, xml):
        """Gets the items from the RSS feed
        """
        results = []
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
        self._last_rss_feed = self._rss_feed

        dom = parseString(xml)
        rssnode = None
        for node in dom.childNodes:
            if node.nodeName == u'rss' or node.nodeName == u'rdf:RDF':
                rssnode = node
        if not rssnode:
            raise Exception, 'RSS format not supported!'
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
