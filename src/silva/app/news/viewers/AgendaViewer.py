# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime, date
from icalendar.interfaces import ICalendar
import calendar
import localdatetime

from five import grok
from zope.cachedescriptors.property import Lazy
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.browser import absoluteURL

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
from silva.app.news.interfaces import IAgendaViewer, IAgendaFilter
from silva.app.news.interfaces import IAgendaItemContentVersion
from silva.app.news.interfaces import get_default_tz_name
from silva.app.news.interfaces import make_filters_source
from silva.app.news.viewers.NewsViewer import NewsViewer, INewsViewerFields
from silva.app.news.htmlcalendar import HTMLCalendar
from Products.SilvaExternalSources.ExternalSource import ExternalSource


_ = MessageFactory('silva_news')


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

    _hide_expired_events=False
    _number_is_days = True
    _number_to_show = 31

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_html')
    def to_html(self, content, request, **parameters):
        """ External Source rendering """
        view = getMultiAdapter((self, request), name='external_source')
        view.document = content.get_content()
        view.parameters = parameters
        return view()

InitializeClass(AgendaViewer)


class AgendaViewerAddForm(silvaforms.SMIAddForm):
    grok.context(IAgendaViewer)
    grok.name(u"Silva Agenda Viewer")

    fields = silvaforms.Fields(ITitledContent, INewsViewerFields).omit('hide_expired_events')
    fields['number_is_days'].mode = u'radio'
    fields['timezone_name'].defaultValue = get_default_tz_name
    fields['filters'].valueField.source = make_filters_source(IAgendaFilter)


class AgendaViewerEditForm(silvaforms.SMIEditForm):
    """ Edit form for news viewer
    """
    grok.context(IAgendaViewer)

    fields = silvaforms.Fields(ITitledContent, INewsViewerFields).omit('id', 'hide_expired_events')
    fields['number_is_days'].mode = u'radio'
    fields['timezone_name'].defaultValue = get_default_tz_name
    fields['filters'].valueField.source = make_filters_source(IAgendaFilter)


class ICalendarResources(IDefaultBrowserLayer):
    silvaconf.resource('calendar.css')


def serialize_date(date):
    return date.strftime('%Y-%m-%d')


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

    @Lazy
    def viewer_url(self):
        return absoluteURL(self.context, self.request)

    def validate_boundaries(self, now, year):
        min_year = now.year - self.YEAR_MAX_DELTA
        max_year = now.year + self.YEAR_MAX_DELTA
        if max_year < year or min_year > year:
            raise BadRequest('Invalid year.')

    def build_calendar(self, current_day, start, end, today=None):
        """ Build a HTMLCalendar where :

        - `current_day` (date) is the selected day
        - `start` (datetime) and `end` (datetime)
           is the range for loading the events
        - `today` (date) defaults to today
        """
        now = datetime.now(self.context.get_timezone())
        today = today or now.date()
        self.validate_boundaries(now, start.year)
        self.validate_boundaries(now, end.year)
        self.__index = {}

        calendar = HTMLCalendar(
            self.context.get_first_weekday(),
            today=today,
            current_day=current_day or today,
            day_render_callback=self._render_day_callback)
        for brain in self.context.get_items_by_date_range(start, end):
            item = brain.getObject()
            if IAgendaItemContentVersion.providedBy(item):
                self._add_event(calendar, item, start, end)
        return calendar

    def _add_event(self, acalendar, event, start, end):
        """ index all the days for which the event has an occurrence between
        start and end.
        """
        timezone = self.context.get_timezone()
        for occurrence in event.get_occurrences():
            cd = occurrence.get_calendar_datetime()
            for datetime_range in cd.get_datetime_ranges(start, end):
                for day in datetimeutils.DayWalk(
                    datetime_range[0], datetime_range[1], timezone):
                    self.__index[serialize_date(day)] = True

    def _render_day_callback(self, day, weekday, week, year, month):
        """Callback for the html calendar to render every day"""
        try:
            event_date = date(year, month, day)
            events = self.__index.get(serialize_date(event_date))
            if events:
                return (
                    'event',
                    '<a href="%s?day=%d&amp;month=%d&amp;year=%d">%d</a>' % \
                        (self.viewer_url, day, month, year, day))
        except ValueError:
            pass
        return (u'',
                unicode(day))


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

    def get_int_param(self, name, default=None):
        try:
            value = self.request.get(name, default)
            if value:
                return int(value)
            return default
        except (TypeError, ValueError):
            return default

    def get_selected_day(self, now=None):
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
        self.selected_month = self.get_int_param('month', self.now.month)
        self.selected_year = self.get_int_param('year', self.now.year)
        try:
            self.selected_day = datetime(
                self.selected_year,
                self.selected_month,
                self.get_selected_day(self.now),
                tzinfo=self.context.get_timezone())
        except ValueError:
            self.selected_day = self.now
            self.selected_year = self.now.year
            self.selected_month = self.now.month

        self.start = datetimeutils.start_of_month(self.selected_day)
        self.end = datetimeutils.end_of_month(self.selected_day)

        self._day_events = self._selected_day_events()
        self.calendar = self.build_calendar(
            self.selected_day.date(), self.start, self.end, self.now.date())

        if self.should_display_prev_link():
            self.calendar.prev_link = \
                '<a class="prevmonth caljump" href="%s">&lt;</a>' % \
                    self.prev_month_url()
        if self.should_display_next_link():
            self.calendar.next_link = \
                '<a class="nextmonth caljump" href="%s">&gt;</a>' % \
                    self.next_month_url()

    def _selected_day_events(self):
        return map(
            lambda b: b.getObject().get_content(),
            self.context.get_items_by_date_range(
                datetimeutils.start_of_day(self.selected_day),
                datetimeutils.end_of_day(self.selected_day)))

    def next_month_url(self):
        year = self.start.year
        month = self.start.month + 1
        if month == 13:
            month = 1
            year = year + 1
        return "%s?month=%d&amp;year=%d&amp;day=1" % (
            self.viewer_url, month, year)

    def prev_month_url(self):
        year = self.start.year
        month = self.start.month - 1
        if month == 0:
            month = 12
            year = year - 1
        return "%s?month=%d&amp;year=%d&amp;day=1" % (
                self.viewer_url, month, year)

    def introduction(self):
        # XXX Should not be done with the method of the Service (who
        # manages settings on how to display the date ?)
        date = localdatetime.get_formatted_date(
            self.selected_day, size="full",
            request=self.request, display_time=False)
        if self._day_events:
            return _(u"Events for ${date}", mapping=dict(date=date))
        return _(u"No events for ${date}", mapping=dict(date=date))

    @property
    def day_events(self):
        return self._day_events

    def render_calendar(self):
        return self.calendar.formatmonth(
            self.selected_year, self.selected_month)

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
