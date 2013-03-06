# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.i18nmessageid import MessageFactory

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from zeam.form import silva as silvaforms
from zeam.utils import batch

# SilvaNews
from ..interfaces import IAgendaFilter, IAgendaItemContentVersion
from .Filter import Filter, IFilterFields
from .NewsFilter import NewsFilterItems

_ = MessageFactory('silva_news')


class AgendaFilter(Filter):
    """To enable editors to channel newsitems on a site, all items
       are passed from NewsFolder to NewsViewer through filters. On a filter
       you can choose which NewsFolders you want to channel items for and
       filter the items on several criteria (as well as individually).
    """
    grok.implements(IAgendaFilter)
    meta_type = "Silva Agenda Filter"
    security = ClassSecurityInfo()

    silvaconf.icon("www/agenda_filter.png")
    silvaconf.priority(3.4)

    security.declarePrivate('get_allowed_types')
    def get_allowed_types(self):
        """Returns the allowed meta_types for this filter"""
        return {'requires': [IAgendaItemContentVersion,]}


InitializeClass(AgendaFilter)


class AgendaFilterAddForm(silvaforms.SMIAddForm):
    grok.context(IAgendaFilter)
    grok.name(u"Silva Agenda Filter")

    fields = silvaforms.Fields(ITitledContent, IFilterFields)


class AgendaFilterEditForm(silvaforms.SMIEditForm):
    """ Base form for filters """
    grok.context(IAgendaFilter)

    fields = silvaforms.Fields(ITitledContent, IFilterFields).omit('id')


class AgendaFilterItems(NewsFilterItems):
    grok.context(IAgendaFilter)
    batchFactory = batch.DateBatch
    batchSize = batch.BATCH_MONTH

    def getItems(self):

        def getter(date):
            return self.context._get_items_by_date(
                date.month, date.year,
                public_only=False, filter_items=False)

        return getter


