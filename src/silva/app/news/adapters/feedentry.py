# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.interface import Interface
from silva.app.document import feed
from silva.app.news.interfaces import INewsItem, IAgendaItem


class NewsItemFeedEntryAdapter(feed.DocumentFeedEntry):
    """Adapter for Silva News Items (article, agenda) to get an atom/rss feed entry 
    representation."""
    grok.adapts(INewsItem, Interface)

    def date_published(self):
        """ This field is used for ordering.
        """
        return self.version.get_display_datetime()


class AgendaItemFeedEntryAdapter(NewsItemFeedEntryAdapter):
    grok.adapts(IAgendaItem, Interface)

    def location(self):
        return self.version.get_location()

    def start_datetime(self):
        return self.version.get_start_datetime().isoformat()

    def end_datetime(self):
        edt = self.version.get_end_datetime()
        return (edt and edt.isoformat()) or edt


