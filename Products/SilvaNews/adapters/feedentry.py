# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements

from silva.core import conf as silvaconf
from silva.core.interfaces.adapters import IFeedEntry
from Products.SilvaDocument.adapters import feedentry

from Products.SilvaNews.interfaces import INewsItem, IAgendaItem

class NewsItemFeedEntryAdapter(feedentry.DocumentFeedEntryAdapter):
    """Adapter for Silva News Items (article, agenda) to get an atom/rss feed entry 
    representation."""

    implements(IFeedEntry)
    silvaconf.context(INewsItem)

    def html_description(self):
        return self.version.get_intro()

    def date_updated(self):
        return self.version.display_datetime()
    
class AgendaItemFeedEntryAdapter(NewsItemFeedEntryAdapter):
    
    implements(IFeedEntry)
    silvaconf.context(IAgendaItem)

    def location(self):
        return self.version.location()

    def start_datetime(self):
        return self.version.start_datetime().isoformat()

    def end_datetime(self):
        edt = self.version.end_datetime()
        return (edt and edt.isoformat()) or edt
