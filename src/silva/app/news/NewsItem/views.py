# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import localdatetime

from datetime import datetime
from five import grok
from zope.component import getUtility, queryMultiAdapter
from zope.cachedescriptors.property import Lazy

from ..interfaces import INewsItem, INewsItemContent

from silva.app.document.interfaces import IDocumentDetails
from silva.core.views import views as silvaviews
from silva.core.services.interfaces import IMetadataService


class NewsItemBaseView(silvaviews.View):
    """Base view on a news or agenda item.
    """
    grok.context(INewsItemContent)
    grok.baseclass()

    @Lazy
    def title(self):
        return self.content.get_title()

    @Lazy
    def publication_date(self):
        date = self.content.get_display_datetime()
        if not date:
            date = getUtility(IMetadataService).getMetadataValue(
                self.content, 'silva-extra', 'publicationtime')
        if date:
            if not isinstance(date, datetime):
                date = date.asdatetime()
            local_months = localdatetime.get_month_names(self.request)
            return u'%s.%s.%s, %s:%s' % (date.day,
                                         local_months[date.month-1],
                                         date.year,
                                         '%02d' % (date.hour),
                                         '%02d' % (date.minute))
        return u''


class NewsItemView(NewsItemBaseView):
    """Base view for an agenda item.
    """
    grok.context(INewsItem)

    @Lazy
    def document(self):
        if self.content is not None:
            return self.content.body.render(self.content, self.request)
        return u''


class NewsItemListItemView(NewsItemBaseView):
    """ Render as a list items (search results)
    """
    grok.context(INewsItemContent)
    grok.name('search_result')

    @Lazy
    def details(self):
        return queryMultiAdapter(
            (self.content, self.request), IDocumentDetails)
