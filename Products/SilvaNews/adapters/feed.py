from cgi import escape
from five import grok
from DateTime import DateTime

from silva.core.interfaces.adapters import IFeedEntry, IFeedEntryProvider
from Products.Silva.browser import feed
from Products.SilvaNews.interfaces import (INewsViewer,
    IAggregator, INewsPublication)
from Products.Silva.browser.feed import ContainerFeedProvider


class NewsPublicationFeedEntryProvider(ContainerFeedProvider):
    grok.context(INewsPublication)

    def entries(self):
        default = self.context.get_default()
        if default and INewsViewer.providedBy(default):
            return IFeedEntryProvider(default).entries()
        return super(self.__class__, self).entries()


class NewsViewerFeedEntryProvider(grok.Adapter):
    grok.context(INewsViewer)
    grok.implements(IFeedEntryProvider)

    def entries(self):
        items = self.context.get_items()
        for item in items:
            if item.get_viewable() is None:
                continue
            entry = IFeedEntry(item, None)
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

    def __init__(self, item):
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


class AggregatorFeedProvider(grok.Adapter):
    grok.context(IAggregator)
    grok.implements(IFeedEntryProvider)

    def entries(self):
        items = self.context.get_merged_feed_contents()

        for item in items:
            entry = AggregatorFeedEntry(item)
            yield entry

