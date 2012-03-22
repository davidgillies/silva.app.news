# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import time
import feedparser

from five import grok
from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem

from Products.Silva import SilvaPermissions
from Products.Silva.Content import Content
from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from silva.core.views import views as silvaviews
from zeam.form import silva as silvaforms

# SilvaNews
from silva.app.news.interfaces import IRSSAggregator

_ = MessageFactory('silva_news')


class RSSAggregator(Content, SimpleItem):
    """The aggregator is used to display content from RSS feeds,
       either from Silva or from extenal sites. One or more feeds are
       merged into a listing for public presentation. The titles and
       leads of items in the feeds are displayed together with a link
       to the original article.
    """
    security = ClassSecurityInfo()

    meta_type = 'Silva RSS Aggregator'
    grok.implements(IRSSAggregator)
    silvaconf.icon("www/rss_aggregator.png")
    silvaconf.priority(3.5)

    def __init__(self, id):
        super(RSSAggregator, self).__init__(id)
        self._rss_feeds = []
        self._last_updated = 0
        self._caching_period = 360 # in seconds
        self._v_cache = None

    # MANIPULATORS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_feeds')
    def set_feeds(self, rss_feeds):
        self._v_cache = None
        self._rss_feeds = list(rss_feeds)
        self._rss_feeds.sort()

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_feeds')
    def get_feeds(self):
        return self._rss_feeds

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_feed_contents')
    def get_feed_contents(self):
        """Return the contents of all given feeds in a dict.

        keys are the feeds set with set_feeds, values are dicts describing
        the feeds content.
        """
        now = time.time()
        last = now - self._caching_period
        cache = getattr(self, '_v_cache', None)
        if cache is None or cache[0] < last:
            # cache needs to be rebuilt
            ret = self._read_feeds()
            self._v_cache = (now, ret)
        else:
            # deliver cached result
            ret = cache[1]
        return ret

    def _read_feeds(self):
        ret = {}
        for feed in self._rss_feeds:
            res = feedparser.parse(feed)
            ret[feed] = res
        return ret

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation,
        'get_merged_feed_contents')
    def get_merged_feed_contents(self):
        feed_data = self.get_feed_contents()
        ret = []
        for uri, channel in feed_data.items():
            for item in channel['items']:
                item['parent_channel'] = {
                    'title':channel['feed']['title'],
                    'link':channel['feed'].get('link',uri)}
                ret.append((item.get('date_parsed',None),item))
        ret.sort(reverse=True)
        return [ r[1] for r in ret ]


InitializeClass(RSSAggregator)


class IRSSAggregatorFields(Interface):
    feeds = schema.List(
        value_type=schema.TextLine(),
        title=_(u'feeds'),
        description=_(u'List the URLs of RSS feeds (one per line) '
                      u'to use as sources of news items.'))


class RSSAggregatorAddForm(silvaforms.SMIAddForm):
    grok.context(IRSSAggregator)
    grok.name(u'Silva RSS Aggregator')

    fields = silvaforms.Fields(ITitledContent, IRSSAggregatorFields)
    fields['feeds'].allowOrdering = False


class RSSAggregatorEditForm(silvaforms.SMIEditForm):
    """ Edit form for RSS aggregators
    """
    grok.context(IRSSAggregator)
    fields = silvaforms.Fields(ITitledContent, IRSSAggregatorFields).omit('id')
    fields['feeds'].allowOrdering = False


class RSSAggregatorView(silvaviews.View):
    grok.context(IRSSAggregator)

    def update(self):
        self.items = self.context.get_merged_feed_contents()


