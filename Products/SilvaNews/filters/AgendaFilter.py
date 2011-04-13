# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import schema
from zope.i18nmessageid import MessageFactory

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass # Zope 2.12

from datetime import datetime

# SilvaNews
from Products.Silva import SilvaPermissions
from Products.SilvaNews.datetimeutils import UTC, local_timezone
from Products.SilvaNews.filters.NewsItemFilter import NewsItemFilter
from Products.SilvaNews.interfaces import (IAgendaFilter, IAgendaItem,
    INewsQualifiers, news_source)
from Products.SilvaNews import datetimeutils

from five import grok
from silva.core import conf as silvaconf
from zeam.form import silva as silvaforms

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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items_by_date')
    def get_items_by_date(self, month, year, meta_types=None,
            timezone=local_timezone):
        """
        Returns non-excluded published items for a particular
        publication month
        """
        sources = self.get_sources()
        if not sources:
            return []

        month = int(month)
        year = int(year)
        startdate = datetime(year, month, 1, tzinfo=timezone).astimezone(UTC)
        endmonth = month + 1
        if month == 12:
            endmonth = 1
            year = year + 1
        enddate = datetime(year, endmonth, 1, tzinfo=timezone).astimezone(UTC)
        return self.get_items_by_date_range(startdate, enddate)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'backend_get_items_by_date')
    def backend_get_items_by_date(self, month, year, meta_types=None,
            timezone=local_timezone):
        """Returns all published items for a particular month
        """
        sources = self.get_sources()
        if not sources:
            return []

        month = int(month)
        year = int(year)
        startdate = datetimeutils.start_of_month(
            datetime(year, month, 1, tzinfo=timezone))
        enddate = datetimeutils.end_of_month(startdate)

        # end dt first
        query = self._prepare_query()
        query['sort_order'] = 'ascending'
        query['sort_on'] = 'end_datetime'
        query['timestamp_ranges'] = {'query': (startdate, enddate)}
        query['sort_on'] = 'start_datetime'

        return self._query_items(**query)

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
