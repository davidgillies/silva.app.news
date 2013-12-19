# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import localdatetime

from icalendar import Calendar
from icalendar.interfaces import IEvent

# ztk
from five import grok
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.cachedescriptors.property import Lazy
from zope.publisher.interfaces.browser import IBrowserRequest

# Silva
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import ResponseHeaders
from silva.app.document.interfaces import IDocumentDetails

# SilvaNews
from ..interfaces import INewsViewer
from ..interfaces import IAgendaItem, IAgendaItemContent
from ..NewsItem.views import (NewsItemBaseView,
                              NewsItemView, NewsItemListItemView)
from ..datetimeutils import RRuleData


class AgendaItemBaseView(silvaviews.View):
    """ Index view for agenda items """
    grok.context(IAgendaItem)
    grok.baseclass()

    @Lazy
    def month_names(self):
        return localdatetime.get_month_names(self.request)

    def format_date(self, date, with_hours=True):
        formatted = u'%s.%s.%s' % (
            date.day, self.month_names[date.month-1], date.year)
        if with_hours:
            formatted += u', %s:%s' % (
                '%02d' % date.hour, '%02d' % date.minute)
        return formatted

    def occurrences(self):
        for occurrence in self.content.get_occurrences():
            timezone = occurrence.get_timezone()
            with_hours = not occurrence.is_all_day()

            start = occurrence.get_start_datetime(timezone)
            end = occurrence.get_end_datetime(timezone)
            end_recurrence = occurrence.get_end_recurrence_datetime()

            information = {
                'start': self.format_date(start, with_hours),
                'end': self.format_date(end, with_hours),
                'location': occurrence.get_location(),
                'recurrence_until': None}

            if end_recurrence:
                information.update({
                    'recurrence_until': self.format_date(
                        end_recurrence, with_hours),
                    'recurrence': RRuleData(
                        occurrence.get_recurrence()).get('FREQ')})

            yield information


class AgendaItemView(NewsItemView, AgendaItemBaseView):
    """Render a agenda item as a content.
    """
    grok.context(IAgendaItem)


class AgendaItemListItemView(NewsItemListItemView, AgendaItemBaseView):
    """ Render as a list items (search results)
    """
    grok.context(IAgendaItemContent)
    grok.name('search_result')


class AgendaItemInlineView(NewsItemBaseView):
    """ Inline rendering for calendar event tooltip """
    grok.context(IAgendaItemContent)
    grok.name('tooltip.html')

    @Lazy
    def details(self):
        return queryMultiAdapter(
            (self.content, self.request), IDocumentDetails)

    def render(self):
        if self.details:
            return u'<div>' + self.details.get_introduction() + u"</div>"
        return u''


class AgendaItemICS(silvaviews.View):
    """ Render an ICS event.
    """
    grok.context(IAgendaItemContent)
    grok.require('zope2.View')
    grok.name('event.ics')

    def render(self):
        viewer = INewsViewer(self.context, None)
        factory = getMultiAdapter((self.content, self.request), IEvent)

        cal = Calendar()
        cal.add('prodid', '-//Silva News Calendaring//lonely event//')
        cal.add('version', '2.0')
        for event in factory(viewer):
            cal.add_component(event)
        return cal.as_string()


class AgendaItemICSResponseHeaders(ResponseHeaders):
    grok.adapts(IBrowserRequest, AgendaItemICS)

    def other_headers(self, headers):
        self.response.setHeader(
            'Content-Type', 'text/calendar;charset=utf-8')
