# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.17 $

from zope.interface import implements
from zope.component import getAdapter

# Zope
import Products
from AccessControl import ClassSecurityInfo
try:
    from App.class_init import InitializeClass # Zope 2.12
except ImportError:
    from Globals import InitializeClass # Zope < 2.12

from dateutil import relativedelta
from icalendar.interfaces import ICalendar

# Silva

from silva.core.views import views as silvaviews
from five import grok
import calendar
from datetime import datetime
from datetime import date

from silva.core import conf as silvaconf
from Products.Silva import SilvaPermissions

# SilvaNews
from Products.SilvaNews.datetimeutils import (datetime_with_timezone,
    local_timezone, start_of_day, end_of_day, DayWalk)
from Products.SilvaNews.interfaces import IAgendaItemVersion, IAgendaViewer
from Products.SilvaNews.viewers.NewsViewer import NewsViewer
from Products.SilvaNews.htmlcalendar import HTMLCalendar


class AgendaViewer(NewsViewer):
    """
    Used to show agendaitems on a Silva site. When setting up an
    agendaviewer you can choose which agendafilters it should use to
    get the items from and how long in advance you want the items
    shown. The items will then automatically be retrieved from the
    agendafilter for each request.
    """

    security = ClassSecurityInfo()

    implements(IAgendaViewer)
    silvaconf.icon("www/agenda_viewer.png")
    silvaconf.priority(3.3)

    meta_type = "Silva Agenda Viewer"

    show_in_tocs = 1

    def __init__(self, id):
        AgendaViewer.inheritedAttribute('__init__')(self, id)
        self._days_to_show = 31
        self._number_is_days = True

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'days_to_show')
    def days_to_show(self):
        """Returns number of days to show
        """
        return self._days_to_show

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items')
    def get_items(self):
        """Gets the items from the filters
        """
        func = lambda x: x.get_next_items(self._days_to_show)
        sortattr = None
        if len(self._filters) > 1: 
            sortattr = 'start_datetime'
        return self._get_items_helper(func,sortattr)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items_by_date')
    def get_items_by_date(self, month, year):
        """Gets the items from the filters
        """
        func = lambda x: x.get_agenda_items_by_date(month,year)
        sortattr = None
        if len(self._filters) > 1: 
            sortattr = 'start_datetime'
        results = self._get_items_helper(func,sortattr)
        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'search_items')
    def search_items(self, keywords):
        """Search the items in the filters
        """
        allowed_meta_types = self.get_allowed_meta_types()
        func = lambda x: x.search_items(keywords,allowed_meta_types)
        sortattr = None
        if len(self._filters) > 1: 
            sortattr = 'start_datetime'
        results = self._get_items_helper(func,sortattr)
        return results

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this Viewer"""
        """results are passed to the filters, some of which may be
           news filters -- don't want to return PlainNewsItems"""
        allowed = []
        mts = Products.meta_types
        for mt in mts:
            if (mt.has_key('instance') and
                IAgendaItemVersion.implementedBy(mt['instance'])):
                allowed.append(mt['name'])
        return allowed

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_days_to_show')
    def set_days_to_show(self, number):
        """Sets the number of days to show in the agenda
        """
        self._days_to_show = number

InitializeClass(AgendaViewer)

class AgendaViewerMonthCalendar(silvaviews.Page):

    grok.context(IAgendaViewer)
    grok.name('month_calendar')
    template = grok.PageTemplateFile(
        filename='../templates/AgendaViewer/month_calendar.pt')

    def update(self):
        now = datetime.now(local_timezone)
        self.calendar = HTMLCalendar()
        self.month = int(self.request.get('month', now.month))
        self.year = int(self.request.get('year', now.year))
        (first_weekday, lastday,) = calendar.monthrange(
            self.year, self.month)

        self.start = datetime(self.year, self.month, 1, tzinfo=local_timezone)
        self.end = datetime(self.year, self.month, lastday, tzinfo=local_timezone)

        self._month_events = self.context.get_items_by_date(self.month, self.year)
        self._day_events = self._selected_day_events()
        self._events_index = {}

        for event_brain in self._month_events:
            sdt = event_brain.start_datetime.astimezone(local_timezone)
            edt = event_brain.end_datetime.astimezone(local_timezone)

            for day_datetime in DayWalk(sdt, edt):
                key = "%d%02d%02d" % (
                    day_datetime.year, day_datetime.month, day_datetime.day,)
                events = self._events_index.get(key, list())
                events.append(event_brain)
                self._events_index[key] = events
                if len(events) == 1:
                    def callback(year, month, day):
                        return self._render_events(year, month, day)
                    self.calendar.register_day_hook(day_datetime, callback)

    def next_month_url(self):
        year = self.start.year
        month = self.start.month + 1
        if month == 13:
            month = 1
            year = year + 1
        return "%s/month_calendar?month=%d&amp;year=%d" % (
            self.context.absolute_url(), month, year)

    def prev_month_url(self):
        year = self.start.year
        month = self.start.month - 1
        if month == 0:
            month = 12
            year = year - 1
        return "%s/month_calendar?month=%d&amp;year=%d" % (
                self.context.absolute_url(), month, year)

    def subscribe_url(self):
        return "%s/subscribe.html" % self.context.absolute_url()

    def day_events(self):
        return self._day_events

    def render_calendar(self):
        return self.calendar.formatmonth(self.year, self.month)

    def _selected_day_events(self):
        day = self.request.get('day', None)
        if day is None:
            return []
        self.day = int(day)
        day_datetime = datetime(self.year, self.month, self.day,
            tzinfo=local_timezone)
        events = self.context.get_items_by_date_range(
            start_of_day(day_datetime), end_of_day(day_datetime))
        return [event.getObject() for event in events]

    def _render_events(self, year, month, day):
        # key = "%d%02d%02d" % (year, month, day,)
        # events = self._events_index[key]
        html = ""
        return '<a href="?day=%s">%s</a><div class="events">%s</div>' % \
            (day, day, html,)


class AgendarViewerCalendar(grok.View):

    grok.context(IAgendaViewer)
    grok.name('calendar.ics')

    def update(self):
        self.request.response.setHeader('Content-Type', 'text/calendar')
        self.calendar = getAdapter(self.context, ICalendar)

    def render(self):
        return unicode(self.calendar)


class AgendaViewerSubscribeView(silvaviews.Page):

    grok.context(IAgendaViewer)
    grok.name('subscribe.html')
    template = grok.PageTemplate(
        filename="../templates/AgendaViewer/subscribe.pt")

    def calendar_url(self):
        return "%s/calendar.ics" % self.context.absolute_url()


