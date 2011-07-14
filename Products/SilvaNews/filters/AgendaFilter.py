# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from datetime import datetime

from five import grok
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from zeam.form import silva as silvaforms

# SilvaNews
from Products.SilvaNews.filters.NewsItemFilter import NewsItemFilter
from Products.SilvaNews.filters.NewsItemFilter import INewsItemFilterSchema
from Products.SilvaNews.filters.NewsFilter import Items, ItemSelection
from Products.SilvaNews.interfaces import IAgendaFilter, IServiceNews

_ = MessageFactory('silva_news')


class AgendaFilter(NewsItemFilter):
    """To enable editors to channel newsitems on a site, all items
       are passed from NewsFolder to NewsViewer through filters. On a filter
       you can choose which NewsFolders you want to channel items for and
       filter the items on several criteria (as well as individually).
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Agenda Filter"
    grok.implements(IAgendaFilter)
    silvaconf.icon("www/agenda_filter.png")
    silvaconf.priority(3.4)

    _allowed_meta_types = ['Silva Agenda Item']

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this filter"""
        return self._allowed_meta_types


InitializeClass(AgendaFilter)


class AgendaFilterAddForm(silvaforms.SMIAddForm):
    grok.context(IAgendaFilter)
    grok.name(u"Silva Agenda Filter")

    fields = silvaforms.Fields(ITitledContent, INewsItemFilterSchema)


class AgendaFilterEditForm(silvaforms.SMIEditForm):
    """ Base form for filters """
    grok.context(IAgendaFilter)

    fields = silvaforms.Fields(ITitledContent, INewsItemFilterSchema).omit('id')


class AgendaFilterItems(Items):
    grok.context(IAgendaFilter)

    month = None
    year = None

    def update(self):
        if self.month is None or self.year is None:
            now = datetime.now()
            self.month = now.month
            self.year = now.year
        self.abbr_monthes = [None] + getUtility(IServiceNews).get_month_abbrs()
        self.label = _('Items of %s %d') % (
            self.abbr_monthes[self.month], self.year)

    def format_year_month(self, year, month):
        return "%d-%02d" % (year, month)

    def publishTraverse(self, request, name):
        try:
            year, month = name.split("-")
            month = int(month)
            year = int(year)
            if month < 1 or month > 12:
                raise ValueError('invalid month %s' % month)
            self.month = month
            self.year = year
            return self
        except (TypeError, ValueError):
            pass
        return super(Items, self).publishTraverse(request, name)

    def getItems(self):
        return [ItemSelection(c, self.context)
                    for c in self.context._get_items_by_date(
                        self.month, self.year, public_only=False,
                        filter_excluded_items=False)]


