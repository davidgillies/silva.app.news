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

    def occurrences(self):
        local_months = localdatetime.get_month_names(self.request)

        for occurrence in self.content.get_occurrences():
            timezone = occurrence.get_timezone()
            location = occurrence.get_location()
            display_time = not occurrence.is_all_day()

            start = occurrence.get_start_datetime(timezone)
            end = occurrence.get_end_datetime(timezone)
            rec_til = occurrence.get_end_recurrence_datetime()

            start_str = u'%s.%s.%s' % (start.day,
                                       local_months[start.month-1],
                                       start.year)

            end_str = u'%s.%s.%s' % (end.day,
                                     local_months[end.month-1],
                                     end.year)

            if display_time:
                start_str = u'%s, %s:%s' % (start_str,
                                            '%02d' % (start.hour),
                                            '%02d' % (start.minute))
                end_str = u'%s, %s:%s' % (end_str,
                                          '%02d' % (end.hour),
                                          '%02d' % (end.minute))

            odi = {
                'start': start_str,
                'end': end_str,
                'location': location,
                'recurrence_until': rec_til,
            }

            if rec_til:
                rec_til_str = u'%s.%s.%s' % (rec_til.day,
                                             local_months[rec_til.month-1],
                                             rec_til.year)

                if display_time:
                    rec_til_str = u'%s, %s:%s' % (rec_til_str,
                                                  '%02d' % (rec_til.hour),
                                                  '%02d' % (rec_til.minute))

                odi['recurrence_until'] = rec_til_str
                recurrence = RRuleData(occurrence.get_recurrence()).get('FREQ')
                odi['recurrence'] = recurrence

            yield odi


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
