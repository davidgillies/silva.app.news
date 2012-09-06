from cgi import escape
from five import grok
from DateTime import DateTime

from zope.interface import Interface
from zope.component import queryMultiAdapter
from Products.Silva.Folder import feeds

from silva.core.interfaces.adapters import IFeedEntry, IFeedEntryProvider
from silva.app.news.interfaces import INewsViewer, IRSSAggregator
from silva.app.news.interfaces import INewsPublication


class NewsPublicationFeedEntryProvider(grok.MultiAdapter):
    grok.adapts(INewsPublication, Interface)
    grok.provides(IFeedEntryProvider)
    grok.implements(IFeedEntryProvider)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def entries(self):
        default = self.context.get_default()
        if INewsViewer.providedBy(default):
            provider = queryMultiAdapter(
                (default, self.request), IFeedEntryProvider)
            for entry in provider.entries():
                yield entry


class NewsViewerFeedEntryProvider(grok.MultiAdapter):
    grok.adapts(INewsViewer, Interface)
    grok.implements(IFeedEntryProvider)
    grok.provides(IFeedEntryProvider)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def entries(self):
        for brain in self.context.get_items():
            item = brain.getObject()
            entry = queryMultiAdapter((item, self.request), IFeedEntry)
            if not entry is None:
                yield entry


class RSS(feeds.RSS):
    """ Rss feed
    """
    grok.context(INewsViewer)
    grok.template('rss')


class Atom(feeds.Atom):
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
        return self.item['description']

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
    grok.adapts(IRSSAggregator, Interface)
    grok.implements(IFeedEntryProvider)

    def entries(self):
        items = self.context.get_merged_feed_contents()

        for item in items:
            entry = AggregatorFeedEntry(item)
            yield entry

