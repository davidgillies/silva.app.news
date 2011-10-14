# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from icalendar import Calendar
from icalendar.interfaces import IEvent

# ztk
from five import grok
from zope.component import getUtility, getMultiAdapter

# Silva
from silva.core.views import views as silvaviews

# SilvaNews
from silva.app.document.interfaces import IDocumentDetails
from silva.app.news.interfaces import INewsViewer, IAgendaItem
from silva.app.news.interfaces import IServiceNews
from silva.app.news.NewsItem.views import NewsItemView


class AgendaItemView(NewsItemView):
    """ Index view for agenda items """
    grok.context(IAgendaItem)

    def occurrences(self):
        format = getUtility(IServiceNews).format_date
        for occurrence in self.content.get_occurrences():
            timezone = occurrence.get_timezone()
            yield {'start': format(occurrence.get_start_datetime(timezone),
                                   occurrence.is_all_day()),
                   'end': format(occurrence.get_end_datetime(timezone),
                                 occurrence.is_all_day()),
                   'location': occurrence.get_location()}


class AgendaItemListItemView(AgendaItemView):
    """ Render as a list items (search results)
    """
    grok.context(IAgendaItem)
    grok.name('search_result')


class AgendaItemInlineView(silvaviews.View):
    """ Inline rendering for calendar event tooltip """
    grok.context(IAgendaItem)
    grok.name('tooltip.html')

    def render(self):
        details = getMultiAdapter(
            (self.content, self.request), IDocumentDetails)
        return u'<div>' + details.get_introduction() + u"</div>"


class AgendaItemICS(silvaviews.View):
    """ Render an ICS event.
    """
    grok.context(IAgendaItem)
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
        self.response.setHeader(
            'Content-Type', 'text/calendar; charset=UTF-8')
        return cal.as_string()
