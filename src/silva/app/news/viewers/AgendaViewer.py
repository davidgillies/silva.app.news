# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime, date
from icalendar.interfaces import ICalendar
import calendar
import localdatetime

from five import grok
from zope.cachedescriptors.property import CachedProperty
from zope.component import getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.browser import absoluteURL
from zope.publisher.interfaces.browser import IBrowserRequest

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from zExceptions import BadRequest

# Silva
from Products.Silva import SilvaPermissions
from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import ResponseHeaders
from silva.fanstatic import need
from zeam.form import silva as silvaforms

from js import jquery

# SilvaNews
from silva.app.news import datetimeutils
from silva.app.news.interfaces import IAgendaViewer
from silva.app.news.interfaces import get_default_tz_name
from silva.app.news.viewers.NewsViewer import NewsViewer, INewsViewerFields
from silva.app.news.htmlcalendar import HTMLCalendar
from Products.SilvaExternalSources.ExternalSource import ExternalSource


class AgendaViewer(NewsViewer, ExternalSource):
    """
    Used to show agendaitems on a Silva site. When setting up an
    agendaviewer you can choose which agendafilters it should use to
    get the items from and how long in advance you want the items
    shown. The items will then automatically be retrieved from the
    agendafilter for each request.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Agenda Viewer"
    grok.implements(IAgendaViewer)
    silvaconf.icon("www/agenda_viewer.png")
    silvaconf.priority(3.3)

    def __init__(self, id):
        super(AgendaViewer, self).__init__(id)
        self._days_to_show = 31
        self._number_is_days = True

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'days_to_show')
    def days_to_show(self):
        """Returns number of days to show
        """
        return self._days_to_show

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_days_to_show')
    def set_days_to_show(self, number):
        """Sets the number of days to show in the agenda
        """
        self._days_to_show = number

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items')
    def get_items(self):
        """Gets the items from the filters
        """
        return self._get_items(
            lambda x: x.get_next_items(self._days_to_show))

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_html')
    def to_html(self, content, request, **parameters):
        """ External Source rendering """
        view = getMultiAdapter((self, request), name='external_source')
        view.document = content.get_content()
        view.parameters = parameters
        return view()

InitializeClass(AgendaViewer)


class ICalendarResources(IDefaultBrowserLayer):
    silvaconf.resource('calendar.css')


class AgendaViewerAddForm(silvaforms.SMIAddForm):
    grok.context(IAgendaViewer)
    grok.name(u"Silva Agenda Viewer")

    fields = silvaforms.Fields(ITitledContent, INewsViewerFields)
    fields['number_is_days'].mode = u'radio'
    fields['timezone_name'].defaultValue = get_default_tz_name


class CalendarView(object):
    """Mixin for AgendaViewer view to help building HTML calendars

    The mixin provides a `build_calendar` method that fetches events
    from `start` to `end` and index them to help the rendering of a particular
    day in the calendar.

    Each time the calendar try to render a day, it calls `_render_day_callback`
    that allows to customize the rendering of a particular day. Events for that
    day are available in the index.
    """

    YEAR_MAX_DELTA = 5

    _events_index = {}

    def validate_boundaries(self, now, year):
        min_year = now.year - self.YEAR_MAX_DELTA
        max_year = now.year + self.YEAR_MAX_DELTA
        if max_year < year or min_year > year:
            raise BadRequest('Invalid year.')

    @staticmethod
    def serialize_date(date):
        return date.strftime('%Y-%m-%d')

    def build_calendar(self, current_day, start, end,
                       today=None, store_events_in_index=False):
        """ Build a HTMLCalendar where :

        - `current_day` (date) is the selected day
        - `today` (date) defaults to today
        - `start` (datetime) and `end` (datetime)
           is the range for loading the events
        - `store_events_in_index` determine if event are stored in index
        or just the fact that a event is present.
        """
        self._store_events_in_index = store_events_in_index
        now = datetime.now(self.context.get_timezone())
        today = today or now.date()
        self.validate_boundaries(now, start.year)
        self.validate_boundaries(now, end.year)

        acalendar = HTMLCalendar(
            self.context.get_first_weekday(),
            today=today,
            current_day=current_day or today,
            day_render_callback=self._render_day_callback)
        for brain in self.context.get_items_by_date_range(start, end):
            self._register_event(acalendar, brain.getObject(), start, end)
        return acalendar

    def _register_event(self, acalendar, event, start, end):
        """ index all the days for which the event has an occurrence between
        start and end.
        """
        for occurrence in event.get_occurrences():
            cd = occurrence.get_calendar_datetime()
            for datetime_range in cd.get_datetime_ranges(start, end):
                for day in datetimeutils.DayWalk(
                    datetime_range[0], datetime_range[1],
                    self.context.get_timezone()):
                    self._index_event(day, event)

    def _index_event(self, adate, event):
        """ (internal) actual indexing of an event.
        """
        serial = self.serialize_date(adate)
        if self._store_events_in_index:
            day_events = self._events_index.get(serial, [])
            day_events.append(event)
            self._events_index[serial] = day_events
        else:
            self._events_index[serial] = True

    def _render_day_callback(self, day, weekday, week, year, month):
        """Callback for the html calendar to render every day"""
        try:
            event_date = date(year, month, day)
            events = self._events_index.get(self.serialize_date(event_date))
            if events:
                return self._render_events(event_date, events)
        except ValueError:
            pass
        return u'', unicode(day)

    def _render_events(self, date, events):
        """render a day for which there is events in the index"""
        cal_url = absoluteURL(self.context, self.request)
        return ('event',
                '<a href="%s?day=%d&amp;month=%d&amp;year=%d">%d</a>' % \
            (cal_url, date.day, date.month, date.year, date.day))


class AgendaViewerExternalSourceView(silvaviews.View, CalendarView):
    """
    Month calendar to be rendered as external source inside a
    Silva Document
    """
    grok.context(IAgendaViewer)
    grok.name('external_source')

    document = None
    parameters = {}

    def update(self):
        timezone = self.context.get_timezone()
        today = datetime.now(timezone).date()

        self.year = today.year
        self.month = today.month

        firstweekday, lastday = calendar.monthrange(
            self.year, self.month)

        self.start = datetime(self.year, self.month, 1, tzinfo=timezone)
        self.end = datetime(self.year, self.month, lastday, 23, 59, 59,
                       tzinfo=timezone)

        self.calendar = self.build_calendar(
            today, self.start, self.end, today=today)

    def render(self):
        return self.calendar.formatmonth(self.year, self.month)


_marker = object()


class AgendaViewerMonthCalendar(silvaviews.View, CalendarView):
    """ View with month calendar and listing of event registered of the
    selected day"""
    grok.context(IAgendaViewer)

    @CachedProperty
    def context_absolute_url(self):
        return absoluteURL(self.context, self.request)

    def get_int_param(self, name, default=None):
        try:
            value = self.request.get(name, default)
            if value:
                return int(value)
            return default
        except (TypeError, ValueError):
            return default

    def get_current_day(self, now=None):
        if now is None:
            now = datetime.now(self.context.get_timezone())
        day = self.get_int_param('day')
        if day is not None:
            return day

        if (self.request.get('month', _marker) is _marker and
                self.request.get('year', _marker) is _marker):
            return now.day
        return 1

    def update(self):
        need(ICalendarResources)
        self.now = datetime.now(self.context.get_timezone())
        self.month = self.get_int_param('month', self.now.month)
        self.year = self.get_int_param('year', self.now.year)
        self.day = self.get_current_day(self.now)
        try:
            self.day_datetime = datetime(self.year, self.month, self.day,
                                     tzinfo=self.context.get_timezone())
        except ValueError:
            self.day_datetime = self.now
            self.year = self.now.year
            self.month = self.now.month
            self.day = self.now.day

        (first_weekday, lastday,) = calendar.monthrange(
            self.year, self.month)

        self.start = datetimeutils.start_of_month(self.day_datetime)
        self.end = datetimeutils.end_of_month(self.day_datetime)

        self._day_events = self._selected_day_events()
        self.calendar = self.build_calendar(
            self.day_datetime.date(), self.start, self.end, self.now.date())

        self._set_calendar_nav()

    def next_month_url(self):
        year = self.start.year
        month = self.start.month + 1
        if month == 13:
            month = 1
            year = year + 1
        return "%s?month=%d&amp;year=%d&amp;day=1" % (
            self.context_absolute_url, month, year)

    def prev_month_url(self):
        year = self.start.year
        month = self.start.month - 1
        if month == 0:
            month = 12
            year = year - 1
        return "%s?month=%d&amp;year=%d&amp;day=1" % (
                self.context_absolute_url, month, year)

    def intro(self):
        # XXX Should not be done with the method of the Service (who
        # manages settings on how to display the date ?)
        dayinfo = u"for %s" % localdatetime.get_formatted_date(
            self.day_datetime, size="full",
            request=self.request, display_time=False)
        if self._day_events:
            return "Events on %s" % dayinfo
        return u"No events on %s" % dayinfo

    @property
    def day_events(self):
        return self._day_events

    def render_calendar(self):
        return self.calendar.formatmonth(self.year, self.month)

    def _selected_day_events(self):
        return map(
            lambda b: b.getObject().get_content(),
            self.context.get_items_by_date_range(
                datetimeutils.start_of_day(self.day_datetime),
                datetimeutils.end_of_day(self.day_datetime)))
 
    def should_display_next_link(self):
        inc, month = divmod(self.start.month, 12)
        year = self.start.year + inc
        return year - self.now.year <= self.YEAR_MAX_DELTA

    def should_display_prev_link(self):
        month = self.start.month - 1
        year = self.start.year
        if month <= 0:
            month = 12
            year -= 1
        return self.now.year - year <= self.YEAR_MAX_DELTA

    def _set_calendar_nav(self):
        if self.should_display_prev_link():
            self.calendar.prev_link = \
                '<a class="prevmonth caljump" href="%s">&lt;</a>' % \
                    self.prev_month_url()
        if self.should_display_next_link():
            self.calendar.next_link = \
                '<a class="nextmonth caljump" href="%s">&gt</a>' % \
                    self.next_month_url()


class AgendaViewerYearCalendar(silvaviews.Page, CalendarView):
    """ Year Calendar representation
    """
    grok.context(IAgendaViewer)
    grok.name('year.html')

    def update(self):
        need(ICalendarResources)
        timezone = self.context.get_timezone()
        now = datetime.now()
        self.year = int(self.request.get('year', now.year))
        self.start = datetime(self.year, 1, 1, tzinfo=timezone)
        self.end = datetimeutils.end_of_year(self.start)
        self.calendar = self.build_calendar(
            self.start.date(), self.start, self.end, now.date())

    def render(self):
        return self.calendar.formatyear(self.year)


class IJSCalendarResources(IDefaultBrowserLayer):
    silvaconf.resource(jquery.jquery)
    silvaconf.resource('fullcalendar/fullcalendar.js')
    silvaconf.resource('calendar.js')
    silvaconf.resource('qtip.js')
    silvaconf.resource('fullcalendar/fullcalendar.css')
    silvaconf.resource('qtip.css')


class AgendaViewerJSCalendar(silvaviews.Page):
    """ Agenda view advanced javascript calendar """
    grok.context(IAgendaViewer)
    grok.name('calendar.html')

    def update(self):
        need(IJSCalendarResources)

    @property
    def events_json_url(self):
        return ''.join((absoluteURL(self.context, self.request),
                        '/++rest++silva.app.news.events'))


class AgendaViewerICSCalendar(silvaviews.View):
    """ Agenda viewer ics format """
    grok.context(IAgendaViewer)
    grok.name('calendar.ics')

    def render(self):
        calendar = getMultiAdapter((self.context, self.request,), ICalendar)
        return calendar.as_string()


class AgendaViewerICSCalendarResponseHeaders(ResponseHeaders):
    grok.adapts(IBrowserRequest, AgendaViewerICSCalendar)

    def other_headers(self, headers):
        self.response.setHeader(
            'Content-Type', 'text/calendar;charset=utf-8')


class AgendaViewerSubscribeView(silvaviews.Page):
    """ View that display the Subcribe url to the calendar """
    grok.context(IAgendaViewer)
    grok.name('subscribe.html')

    def update(self):
        self.request.timezone = self.context.get_timezone()

    def calendar_url(self):
        return "%s/calendar.ics" % absoluteURL(self.context, self.request)

