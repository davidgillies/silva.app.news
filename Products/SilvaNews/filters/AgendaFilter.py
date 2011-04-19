# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.component import getUtility

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass # Zope 2.12

from datetime import datetime

from zeam.utils.batch.interfaces import IBatching
from zeam.utils.batch.batch import batchItemIterator

from five import grok
from silva.core import conf as silvaconf
from zeam.form import silva as silvaforms

# SilvaNews
from Products.SilvaNews.filters.NewsItemFilter import NewsItemFilter
from Products.SilvaNews.filters.NewsFilter import Items
from Products.SilvaNews.interfaces import (IAgendaFilter, IAgendaItem,
    INewsQualifiers, news_source, IServiceNews)

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

    def _is_agenda_addable(self, addable_dict):
        return (
            addable_dict.has_key('instance') and
            IAgendaItem.isImplementedByInstancesOf(
            addable_dict['instance']))

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this filter"""
        return self._allowed_meta_types

InitializeClass(AgendaFilter)


class AgendaFilterAddForm(silvaforms.SMIAddForm):
    grok.context(IAgendaFilter)
    grok.name(u"Silva Agenda Filter")


class IAgendaFilterSchema(INewsQualifiers):
    _keep_to_path = schema.Bool(
        title=_(u"stick to path"))

    sources = schema.Set(
        value_type=schema.Choice(source=news_source),
        title=_(u"sources"),
        description=_(u"Use predefined sources."))


class AgendaFilterEditForm(silvaforms.SMIEditForm):
    """ Base form for filters """
    grok.context(IAgendaFilter)
    fields = silvaforms.Fields(IAgendaFilterSchema)


def next_month(year, month):
    if month == 12:
        return year + 1, 1
    return year, month + 1


def previous_month(year, month):
    if month == 1:
        return year - 1, 12
    return year, month - 1


class YearMonthBatch(object):
    grok.implements(IBatching)

    def __init__(self, collection, year=None, month=None, factory=None):
        self.data = list(collection)
        self.count = len(self.data)
        self.start = 0
        self.first = 0
        self.last = self.count - 1
        self.year = year
        self.month = month
        self.factory = factory
        now = datetime.now()
        if self.year is None:
            self.year = now.year
        if self.month is None:
            self.month = now.month
        self.next = "%s-%s" % next_month(self.year, self.month)
        self.previous = "%s-%s" % previous_month(self.year, self.month)

    def batchLen(self):
        return self.count

    def __iter__(self):
        return batchItemIterator(self, factory=self.factory)

    def all(self):
        return self.__iter__()

    def __getitem__(self, index):
        if index < 0 or index >= self.count:
            raise IndexError, "invalid index"
        return self.data[self.start + index]


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

    def getBatch(self, factory=None):
        return YearMonthBatch(
            self.context._get_items_by_date(
                self.month, self.year, public_only=False,
                filter_excluded_items=False),
            month=self.month, year=self.year, factory=factory)


