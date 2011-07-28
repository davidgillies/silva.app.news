from cgi import escape
from five import grok
from DateTime import DateTime

from zope.interface import Interface
from zope import component

from silva.core.interfaces.adapters import IFeedEntry, IFeedEntryProvider
from Products.Silva.browser import feed
from silva.app.news.interfaces import (INewsViewer,
    IAggregator, INewsPublication)
from Products.Silva.browser.feed import ContainerFeedProvider


class NewsPublicationFeedEntryProvider(ContainerFeedProvider):
    grok.adapts(INewsPublication, Interface)

    def entries(self):
        default = self.context.get_default()
        if default and INewsViewer.providedBy(default):
            return IFeedEntryProvider(default).entries()
        return super(self.__class__, self).entries()


class NewsViewerFeedEntryProvider(grok.MultiAdapter):
    grok.adapts(INewsViewer, Interface)
    grok.implements(IFeedEntryProvider)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def entries(self):
        items = self.context.get_items()
        for item in items:
            if item.get_viewable() is None:
                continue
            entry = component.queryMultiAdapter(
                (item, self.request), IFeedEntry)
            if not entry is None:
                yield entry


class RSS(feed.RSS):
    """ Rss feed
    """
    grok.context(INewsViewer)
    grok.template('rss')


class Atom(feed.Atom):
    """ Atom feed
    """
    grok.context(INewsViewer)
    grok.template('atom')


class AggregatorFeedEntry(object):
    grok.implements(IFeedEntry)

    def __init__(self, item, request):
        self.item = item

    def id(self):
        return escape(self.item['link'], quote=True)

    def title(self):
        titl = self.item['title']
        if self.item['parent_channel']['title']:
            titl += ' [%s]'%self.item['parent_channel']['title']
        return titl

    def html_description(self):
        desc = self.item['description']
        return desc

    def description(self):
        return self.html_description()

    def url(self):
        return self.id()

    def authors(self):
        return []

    def date_updated(self):
        return DateTime(self.item.get('modified'))

    def date_published(self):
        return DateTime(self.item.get('date'))

    def keywords(self):
        return []

    def subject(self):
        return None


class AggregatorFeedProvider(grok.MultiAdapter):
    grok.adapts(IAggregator, Interface)
    grok.implements(IFeedEntryProvider)

    def entries(self):
        items = self.context.get_merged_feed_contents()

        for item in items:
            entry = AggregatorFeedEntry(item)
            yield entry

