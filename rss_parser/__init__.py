"""Parse RSS streams

usage:

l = RSSLoader()
r = l.get_rss(<url>)

get_rss returns a (data containing) object with the following attributes:

Fields that are derived from the channel's plain elements:

    r.title
    r.description
    r.link
    r.copyright
    r.pubdate
    r.lastbuilddate
    r.language
    r.category
    r.webmaster
    r.managingeditor
    r.ttl
    r.rating
    r.docs
    r.generator

Special fields:

    r.image - an object containing the following attributes:

    Image fields:
    
        r.image.url
        r.image.title
        r.image.description
        r.image.link
        r.image.width
        r.image.height

    r.textinput - an object containing the following attributes:

    TestInput fields:

        r.textinput.title
        r.textinput.description
        r.textinput.name
        r.textinput.link

    r.items - a list of item objects

    ItemObject fields:

        item.title
        item.description
        item.link
        item.author
        item.category
        item.comments
        item.enclosure
        item.guid
        item.pubdate
        item.source
        item.sourceurl - reflects the 'url' attribute of the
                item's source element

Meta-fields (used in the caching machinery):

    r.wascached - whether the result was returned from some cache or was retrieved just now
    r.etag - the value of the Etag HTTP response header
    r.last_modified - the value of the Last-Modified HTTP response header
    r.last_checked - the timestamp of the last (uncached) request

The loader has the following additional methods:

    l.set_ttl(<int/float>):
        Sets the time to live period (in minutes). If an (uncached) request was made
        less than ttl minutes ago, the result from that is returned and no new request
        will be made

    l.ttl():
        Returns the current ttl

"""

from rss_parser import *
