# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.publisher.interfaces.http import IHTTPRequest
from zope.cachedescriptors.property import Lazy

from silva.app.document import feed
from silva.app.news.interfaces import INewsItemVersion, IAgendaItemVersion


class NewsItemFeedEntryAdapter(feed.DocumentFeedEntry):
    """Adapter for Silva News Items (article, agenda) to get an
    atom/rss feed entry representation.
    """
    grok.adapts(INewsItemVersion, IHTTPRequest)

    def date_published(self):
        """ This field is used for ordering.
        """
        return self.context.get_display_datetime()


class AgendaItemFeedEntryAdapter(NewsItemFeedEntryAdapter):
    grok.adapts(IAgendaItemVersion, IHTTPRequest)

    @Lazy
    def occurrence(self):
        occurrences = self.context.get_occurrences()
        if len(occurrences):
            return occurrences[0]
        return None

    def location(self):
        if self.occurrence is not None:
            return self.occurrence.get_location()
        return None

    def start_datetime(self):
        if self.occurrence is not None:
            return self.occurrence.get_start_datetime().isoformat()
        return None

    def end_datetime(self):
        if self.occurrence is not None:
            time = self.occurrence.get_end_datetime()
            if time:
                return time.isoformat()
        return None


