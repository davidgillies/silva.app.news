"""Parse RSS streams

usage:

l = RSSLoader()
r = l.get_rss(<url>)

get_rss returns a dict with the following keys:

Fields that are derived from the channel's plain elements:

    title
    description
    link
    copyright
    pubdate
    lastbuilddate
    language
    category
    webmaster
    managingeditor
    ttl
    rating
    docs
    generator

    Note that some of the elements' tagnames are defined with capitals in the RSS protocol,
    but the dict keys of the channel dict uses lowercase

Special fields:

    image - a dict containing the following keys:

    Image fields:
    
        url
        title
        description
        link
        width
        height

    textinput - a dict containing the following attributes:

    TestInput fields:

        title
        description
        name
        link

    items - a list of item dicts

    Item fields:

        title
        description
        link
        author
        category
        comments
        enclosure
        guid
        pubdate
        source
        sourceurl - reflects the 'url' attribute of the
                item's source element

Meta-fields (used in the caching machinery):

    wascached - whether the result was returned from some cache or was retrieved just now
    tag - the value of the Etag HTTP response header
    last_modified - the value of the Last-Modified HTTP response header
    last_checked - the timestamp of the last (uncached) request

The loader has the following additional methods:

    l.set_ttl(<int/float>):
        Sets the time to live period (in minutes). If an (uncached) request was made
        less than ttl minutes ago, the result from that is returned and no new request
        will be made

    l.ttl():
        Returns the current ttl

"""

from rss_parser import *
