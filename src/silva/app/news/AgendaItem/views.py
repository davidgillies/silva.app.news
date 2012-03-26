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
from ..interfaces import IServiceNews, INewsViewer
from ..interfaces import IAgendaItem, IAgendaItemContent
from ..NewsItem.views import NewsItemListItemView, NewsItemView


class AgendaItemBaseView(silvaviews.View):
    """ Index view for agenda items """
    grok.context(IAgendaItem)
    grok.baseclass()

    def occurrences(self):
        format = getUtility(IServiceNews).format_date
        for occurrence in self.content.get_occurrences():
            timezone = occurrence.get_timezone()
            yield {'start': format(occurrence.get_start_datetime(timezone),
                                   occurrence.is_all_day()),
                   'end': format(occurrence.get_end_datetime(timezone),
                                 occurrence.is_all_day()),
                   'location': occurrence.get_location()}


class AgendaItemView(NewsItemView, AgendaItemBaseView):
    """Render a agenda item as a content.
    """
    grok.context(IAgendaItem)



class AgendaItemListItemView(NewsItemListItemView, AgendaItemBaseView):
    """ Render as a list items (search results)
    """
    grok.context(IAgendaItemContent)
    grok.name('search_result')


class AgendaItemInlineView(NewsItemListItemView):
    """ Inline rendering for calendar event tooltip """
    grok.context(IAgendaItemContent)
    grok.name('tooltip.html')

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
        self.response.setHeader(
            'Content-Type', 'text/calendar; charset=UTF-8')
        return cal.as_string()
