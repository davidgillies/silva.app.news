# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from icalendar import vDatetime
from dateutil.rrule import rrulestr

# ztk
from five import grok
from zope.i18nmessageid import MessageFactory
from zope.component import getUtility

from AccessControl import ClassSecurityInfo
from Acquisition import Explicit
from App.class_init import InitializeClass

from Products.Silva import SilvaPermissions

from silva.app.document.document import DocumentContent
from silva.app.document.document import DocumentContentVersion
from silva.core import conf as silvaconf

from ..NewsItem import NewsItemContent, NewsItemContentVersion
from ..NewsItem import NewsItemContentVersionCatalogingAttributes
from ..datetimeutils import CalendarDatetime, get_timezone, RRuleData, UTC
from ..datetimeutils import datetime_with_timezone, datetime_to_unixtimestamp
from ..interfaces import IAgendaItem, IAgendaItemVersion
from ..interfaces import IAgendaItemContent, IAgendaItemContentVersion
from ..interfaces import IServiceNews, IAgendaItemOccurrence


_marker = object()
_ = MessageFactory('silva_news')


class AgendaItemOccurrence(Explicit):
    grok.implements(IAgendaItemOccurrence)
    # This in inherit of Explicit because it did in 2.3 and Explicit
    # is not compatible with object.
    _start_datetime = None
    _end_datetime = None
    _location = ''
    _recurrence = None
    _all_day = False
    _timezone_name = None

    def __init__(self,
                 start_datetime=_marker,
                 end_datetime=_marker,
                 display_time=_marker,
                 location=_marker,
                 all_day=_marker,
                 timezone_name=_marker,
                 recurrence=_marker,
                 end_recurrence_datetime=_marker):

        if timezone_name is not _marker:
            self.set_timezone_name(timezone_name)
            timezone = get_timezone(timezone_name)
        else:
            timezone = get_timezone(None)

        if start_datetime is not _marker:
            start_datetime = start_datetime.replace(tzinfo=timezone)
            self.set_start_datetime(start_datetime)
        if end_datetime is not _marker:
            end_datetime = end_datetime.replace(tzinfo=timezone)
            self.set_end_datetime(end_datetime)
        if display_time is not _marker:
            self.set_display_time(display_time)
        if location is not _marker:
            self.set_location(location)
        if recurrence is not _marker and recurrence:
            recurrence = RRuleData(recurrence)
            if end_recurrence_datetime is not _marker:
                recurrence['UNTIL'] = vDatetime(
                    end_recurrence_datetime.replace(
                        tzinfo=timezone).astimezone(UTC))
            self.set_recurrence(str(recurrence))
        if all_day is not _marker:
            self.set_all_day(all_day)

    def set_timezone_name(self, name):
        self._timezone_name = name

    def get_timezone_name(self):
        timezone_name = self._timezone_name
        if timezone_name is None:
            return getUtility(IServiceNews).get_timezone_name()
        return timezone_name

    def get_timezone(self):
        if not hasattr(self, '_v_timezone'):
            self._v_timezone = get_timezone(self.get_timezone_name())
        return self._v_timezone

    def set_start_datetime(self, value):
        self._start_datetime = datetime_with_timezone(
            value, self.get_timezone())

    def get_start_datetime(self, tz=_marker):
        if tz is _marker:
            tz = self.get_timezone()
        cd = self.get_calendar_datetime()
        if cd:
            return cd.get_start_datetime(tz)
        return None

    def get_calendar_datetime(self):
        if not self._start_datetime:
            return None
        return CalendarDatetime(
            self._start_datetime,
            self._end_datetime,
            recurrence=self.get_rrule())

    def set_end_datetime(self, value):
        self._end_datetime = datetime_with_timezone(
            value, self.get_timezone())

    def get_end_datetime(self, tz=_marker):
        if tz is _marker:
            tz = self.get_timezone()
        cd = self.get_calendar_datetime()
        if cd:
            return cd.get_end_datetime(tz)
        return None

    def set_recurrence(self, recurrence):
        self._recurrence = recurrence

    def get_recurrence(self):
        if self._recurrence is not None:
            return str(self._recurrence)

    def get_end_recurrence_datetime(self):
        if self._recurrence is not None:
            dt_string = RRuleData(self.get_recurrence()).get('UNTIL')
            if dt_string:
                return vDatetime.from_ical(dt_string).\
                    replace(tzinfo=UTC).astimezone(self.get_timezone())

    def get_rrule(self):
        if self._recurrence is not None:
            return rrulestr(str(self._recurrence), dtstart=self._start_datetime)
        return None

    def set_location(self, value):
        self._location = value

    def get_location(self):
        return self._location

    def set_all_day(self, value):
        self._all_day = bool(value)

    def is_all_day(self):
        return self._all_day

    get_all_day = is_all_day


class AgendaItemContentVersion(NewsItemContentVersion):
    grok.baseclass()
    grok.implements(IAgendaItemContentVersion)

    security = ClassSecurityInfo()
    _occurrences = []

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_occurrences')
    def set_occurrences(self, occurrences):
        self._occurrences = occurrences

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_occurrences')
    def get_occurrences(self):
        return map(lambda o: o.__of__(self), self._occurrences)

InitializeClass(AgendaItemContentVersion)


class AgendaItemVersion(AgendaItemContentVersion, DocumentContentVersion):
    """Silva News AgendaItemVersion
    """
    grok.implements(IAgendaItemVersion)
    meta_type = "Silva Agenda Item Version"
    security = ClassSecurityInfo()


InitializeClass(AgendaItemVersion)


class AgendaItemContent(NewsItemContent):
    grok.baseclass()
    grok.implements(IAgendaItemContent)
    security = ClassSecurityInfo()


InitializeClass(AgendaItemContent)


class AgendaItem(AgendaItemContent, DocumentContent):
    """A News item for events. Includes date and location
       metadata, as well settings for subjects and audiences.
    """
    grok.implements(IAgendaItem)
    meta_type = "Silva Agenda Item"
    security = ClassSecurityInfo()
    silvaconf.icon("www/agenda_item.png")
    silvaconf.priority(-6)
    silvaconf.version_class(AgendaItemVersion)


InitializeClass(AgendaItem)


class AgendaItemContentVersionCatalogingAttributes(
    NewsItemContentVersionCatalogingAttributes):
    grok.context(IAgendaItemContentVersion)

    def sort_index(self):
        occurrences = self.context.get_occurrences()
        if len(occurrences):
            dt = occurrences[0].get_start_datetime()
            if dt:
                return datetime_to_unixtimestamp(dt)
        return None

    def timestamp_ranges(self):
        ranges = []
        for occurrence in self.context.get_occurrences():
            ranges.extend(
                occurrence.get_calendar_datetime().get_unixtimestamp_ranges())
        return ranges

