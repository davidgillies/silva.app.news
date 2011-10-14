# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getUtility
from zope.cachedescriptors.property import CachedProperty

from Products.SilvaMetadata.interfaces import IMetadataService
from silva.app.news.interfaces import IServiceNews, INewsItem

from silva.core.views import views as silvaviews


class NewsItemView(silvaviews.View):
    """View on a News Item (either Article / Agenda)
    """
    grok.context(INewsItem)

    @CachedProperty
    def article_date(self):
        article_date = self.content.get_display_datetime()
        if not article_date:
            article_date =  getUtility(IMetadataService).getMetadataValue(
                self.content, 'silva-extra', 'publicationtime')
        if article_date:
            news_service = getUtility(IServiceNews)
            return news_service.format_date(article_date)
        return u''

    @CachedProperty
    def article(self):
        if self.content is not None:
            return self.content.body.render(self.content, self.request)
        return u''


class NewsItemListItemView(NewsItemView):
    """ Render as a list items (search results)
    """
    grok.context(INewsItem)
    grok.name('search_result')

