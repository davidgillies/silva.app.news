#!/usr/bin/env python2.2

from xml.dom.minidom import parseString
import time

from xml_helpers import *
from cached_http_loader import *

# ZOPE
import Acquisition
from AccessControl import ClassSecurityInfo

class FormatException(Exception):
    pass

class RSSParser:
    """An RSS parser

    Parses most elements of RSS feeds versions 0.9, 0.91, 1.0 and 2.0
    """

    def parse_stream(self, xml):
        """Fetches the data from the url if it hasn't been changed

        Sends If-Modified-Since headers and ETag headers to see whether
        it should or should not use cached data.
        """
        retval = {}
        retval['rssitems'] = []
        retval['image'] = {}
        retval['textinput'] = {}
        dom = parseString(xml)

        # first find the namespace and version
        namespace = None
        version = None
        if dom.documentElement.nodeName == u'rss':
            print "Docelement:", dom.documentElement
            print "Dir:", dir(dom.documentElement)
            print "Attrs:", dom.documentElement._attrs
            for attr in dom.documentElement._attrs.keys():
                if attr == u'version':
                    version = dom.documentElement._attrs[attr].nodeValue
        else:
            for attr in dom.documentElement._attrs.keys():
                ns = None
                tag = attr
                if attr.find(':') > -1:
                    tag, ns = attr.split(':')
                if tag == 'xmlns':
                    if (dom.documentElement._attrs[attr].nodeValue == 
                            u'http://purl.org/rss/1.0/'): 
                        namespace = ns
                        version = '1.0'
                        break
                    elif (dom.documentElement._attrs[attr].nodeValue == 
                            u'http://my.netscape.com/rdf/simple/0.9/'):
                        namespace = ns
                        version = '0.9'
                        break

        # so now we know the namespace (if any) and the version
        # get the channel element
        channel = getChildOfName(dom.documentElement, u'channel', namespace)
        if not channel:
            raise FormatException, 'No channel element found!'

        # and parse it
        self.parse_channel(channel, retval, namespace)

        # Some versions of RSS have the items defined outside of the channel, 
        # and some versions even have references in the channel and the items 
        # themselves outside of it.
        # In any case, it looks like if there are items outside of the 
        # channel, we should use them, even if they're also defined in the 
        # channel. So if we have an items section outside of the channel, 
        # throw away any items found in the channel and parse the list found 
        # outside of it.
        item = getChildOfName(dom.documentElement, u'item', namespace)
        if item:
            retval['rssitems'] = []
            self.parse_items(dom.documentElement, retval, namespace)

        # afaik the textinput element can be part of the channel or of the rss
        # main node, so let's try to find it here as well
        textinputnode = getChildOfName(dom.documentElement, u'textinput', 
                            namespace)
        if textinputnode:
            self.parse_textinput(textinputnode, retval, namespace)

        # the same counts for image, can be part of the channel as well 
        # as of the main node
        imagenode = getChildOfName(dom.documentElement, u'image', namespace)
        if imagenode:
            self.parse_image(imagenode, retval, namespace)

        return retval

    def parse_channel(self, channel, retval, namespace):
        """Parse all interesting elements of the channel node
        """
        retval['title']            = getNodeContent(getChildOfName(channel, 
                                                    u'title', 
                                                    namespace))
        retval['description']      = getNodeContent(getChildOfName(channel, 
                                                    u'description', 
                                                    namespace))
        retval['link']             = getNodeContent(getChildOfName(channel, 
                                                    u'link', 
                                                    namespace))
        retval['copyright']        = getNodeContent(getChildOfName(channel, 
                                                    u'copyright', 
                                                    namespace))
        retval['pubdate']          = getNodeContent(getChildOfName(channel, 
                                                    u'pubDate', 
                                                    namespace))
        retval['lastbuilddate']    = getNodeContent(getChildOfName(channel, 
                                                    u'lastBuildDate', 
                                                    namespace))
        retval['language']         = getNodeContent(getChildOfName(channel, 
                                                    u'language', 
                                                    namespace))
        retval['category']         = getNodeContent(getChildOfName(channel, 
                                                    u'category', 
                                                    namespace))
        retval['webmaster']        = getNodeContent(getChildOfName(channel, 
                                                    u'webMaster', 
                                                    namespace))
        retval['managingeditor']   = getNodeContent(getChildOfName(channel, 
                                                    u'managingEditor', 
                                                    namespace))
        retval['ttl']              = getNodeContent(getChildOfName(channel, 
                                                    u'ttl', 
                                                    namespace))
        retval['rating']           = getNodeContent(getChildOfName(channel, 
                                                    u'rating', 
                                                    namespace))
        retval['docs']             = getNodeContent(getChildOfName(channel, 
                                                    u'docs', 
                                                    namespace))
        retval['generator']        = getNodeContent(getChildOfName(channel, 
                                                    u'generator', 
                                                    namespace))

        imagenode = getChildOfName(channel, u'image', namespace)
        if imagenode:
            self.parse_image(imagenode, retval, namespace)
        
        itemsnode = getChildOfName(channel, u'item', namespace)
        if itemsnode:
            self.parse_items(channel, retval, namespace)

        textinputnode = getChildOfName(channel, u'textinput', namespace)
        if textinputnode:
            self.parse_textinput(textinputnode, retval, namespace)

    def parse_image(self, image, retval, namespace):
        """Parse all interesting elements of the image node
        """
        retval['image']['url']         = getNodeContent(
                                         getChildOfName(image, 
                                                        u'url', 
                                                        namespace))
        retval['image']['title']       = getNodeContent(
                                         getChildOfName(image, 
                                                        u'title', 
                                                        namespace))
        retval['image']['description'] = getNodeContent(
                                         getChildOfName(image, 
                                                        u'description', 
                                                        namespace))
        retval['image']['link']        = getNodeContent(
                                         getChildOfName(image, 
                                                        u'link', 
                                                        namespace))

    def parse_items(self, parent, retval, namespace):
        """Oarse the items into the items list
        """
        i = 0
        while 1:
            item = getChildOfName(parent, u'item', namespace, i)
            if not item:
                break
            i += 1
            itemobj = {} 
            itemobj['title']       = getNodeContent(
                                     getChildOfName(item, 
                                                     u'title', 
                                                     namespace))
            itemobj['description'] = getNodeContent(
                                     getChildOfName(item, 
                                                     u'description', 
                                                     namespace))
            itemobj['link']        = getNodeContent(
                                     getChildOfName(item, 
                                                     u'link', 
                                                     namespace))
            itemobj['author']      = getNodeContent(
                                     getChildOfName(item, 
                                                     u'author', 
                                                     namespace))
            itemobj['category']    = getNodeContent(
                                     getChildOfName(item, 
                                                     u'category', 
                                                     namespace))
            itemobj['comments']    = getNodeContent(
                                     getChildOfName(item, 
                                                     u'comments', 
                                                     namespace))
            itemobj['enclosure']   = getNodeContent(
                                     getChildOfName(item, 
                                                     u'enclosure', 
                                                     namespace))
            itemobj['guid']        = getNodeContent(
                                     getChildOfName(item, 
                                                     u'guid', 
                                                     namespace))
            itemobj['pubdate']     = getNodeContent(
                                     getChildOfName(item, 
                                                     u'pubdate', 
                                                     namespace))
            
            sourceel = getChildOfName(item, u'source', namespace)
            if sourceel:
                itemobj['source'] = sourceel.nodeValue
                itemobj['sourceurl'] = sourceel._attrs[u'url'].nodeValue

            retval['rssitems'].append(itemobj)

    def parse_textinput(self, node, retval, namespace):
        """Parse a textinput element
        """
        retval['textinput']['title']       = getNodeContent(
                                             getChildOfName(node, 
                                                            u'title', 
                                                            namespace))
        retval['textinput']['description'] = getNodeContent(
                                             getChildOfName(node, 
                                                            u'description', 
                                                            namespace))
        retval['textinput']['name']        = getNodeContent(
                                             getChildOfName(node, 
                                                            u'name', 
                                                            namespace))
        retval['textinput']['link']        = getNodeContent(
                                             getChildOfName(node,
                                                            u'link', 
                                                            namespace))

class RSSLoader:
    """Gets the data from an URL and parses it

    Caches the result of calls to skip the (costly!)
    parse process if the request was cached anyway.
    """

    def __init__(self):
        self._cache = {}
        self._ttl = None 

    def get_rss(self, url):
        if (self._cache.has_key(url) and 
                self._ttl and
                self._cache[url]['last_checked'] and
                time.time() < self._cache[url]['last_checked'] + (self._ttl * 60)):
            ret = self._cache[url]
            ret['wascached'] = 1
        else:
            l = CachedHTTPLoader()
            r = l.urlopen(url)
            ret = None
            if (r.wascached and 
                    self._cache.has_key(url) and 
                    (self._cache[url]['etag'] == r.etag or 
                    self._cache[url]['last_modified'] == r.last_modified)):
                ret = self._cache[url]
                ret['wascached'] = 1
            else:
                p = RSSParser()
                ret = p.parse_stream(r.read())
                ret['etag'] = r.etag
                ret['last_modified'] = r.last_modified
                ret['last_checked'] = time.time()
                self._cache[url] = ret
                ret['wascached'] = 0

        return ret

    def set_ttl(self, value):
        """Sets the ttl (in minutes)

        If set higher than 0 (default 60) the loader will use cached data
        if the time of the last (non-ceched) request is no longer than <value>
        minutes ago.
        """
        self._ttl = int(value)

    def ttl(self):
        """Returns the ttl
        """
        return self._ttl

if __name__ == '__main__':
    import sys
    if not len(sys.argv) == 2:
        print "Usage: %s <url>" % sys.argv[0]
    else:
        loader = RSSLoader()
        r = loader.get_rss(sys.argv[1])

        print r
