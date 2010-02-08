# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.21 $

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
try:
    from App.class_init import InitializeClass # Zope 2.12
except ImportError:
    from Globals import InitializeClass # Zope < 2.12

# Silva interfaces
from Products.SilvaNews.interfaces import IAgendaItem, IAgendaItemVersion
from Products.SilvaNews.interfaces import INewsItem, INewsItemVersion

# Silva
from silva.core import conf as silvaconf
from Products.Silva import SilvaPermissions
from silva.core.interfaces import IVersionedContent
from Products.Silva.helpers import add_and_edit
from silva.core.services.interfaces import ICataloging
from icalendar import UTC, LocalTimezone
from datetime import date, datetime
from dateutil.rrule import rrule, rruleset
from dateutil.relativedelta import relativedelta

# SilvaNews
from NewsItem import NewsItem, NewsItemVersion

_marker = object()
local_timezope = LocalTimezone()

def to_utc_datetime(aDateTime_or_datetime, end=False):
    if isinstance(aDateTime_or_datetime, date):
        time = {'hour': 0, 'minute': 0,  'second': 0, 'tzinfo': UTC}
        if end:
            time = {'hour': 23,
                    'minute': 59,
                    'second': 59,
                    'microsecond': 99999,
                    'tzinfo': UTC}
        return datetime(aDateTime_or_datetime.year,
            aDateTime_or_datetime.month,
            aDateTime_or_datetime.day,
            **time)
    if isinstance(aDateTime_or_datetime, DateTime):
        return aDateTime_or_datetime.utcdatetime
    if isinstance(aDateTime_or_datetime):
        return datetime_set_timezone(aDateTime_or_datetime).astimezone(UTC)

def datetime_set_timezone():
    if dt.tzinfo is None:
        dt.replace(tzinfo=local_timezone)
    return dt

def datetime_to_unixtimestamp(dt):
    return int(dt.strftime("%s"))

def end_of_day(dt):
    return dt.replace(hour=24, minute=0, second=0)

def start_of_day(dt):
    return dt.replace(hour=0, minute=0, second=0)


class CalendarDateRepresentation(object):

    default_duration = relativedelta(hours=+1)

    def __init__(self, start_datetime,
            end_datetime=None, all_day=False, recurrence=None):

        utc_start_datetime = to_utc_datetime(start_datetime)
        utc_end_datetime = end_datetime and \
            to_utc_datetime(end_datetime, end=True)

        self.all_day = all_day or \
            self.__is_all_day(start_datetime, end_datetime)

        if all_day:
            self.start_datetime = start_of_day(utc_start_datetime)
            if end_datetime is None:
                self.end_datetime = end_of_day(self.start_datetime)
            self.end_datetime = utc_end_datetime and \
                end_of_day(utc_end_datetime)
        else:
            self.start_datetime = utc_start_datetime
            self.end_datetime = utc_end_datetime

        self.validate()

        if recurrence is not None:
            self.set_recurrence(recurrence)

    def get_duration(self):
        if self.end_datetime:
            return relativedelta(self.start_datetime, self.end_datetime)
        return default_duration

    def set_start_datetime(self, value):
        self.start_datetime = to_utc_datetime(value)
        self.validate()
        return self.start_datetime

    def set_end_datetime(self, value):
        self.end_datetime = to_utc_datetime(value)
        self.validate()
        return self.end_datetime

    def validate(self):
        if self.start_datetime is None:
            raise TypeError, 'start datetime can\' be None'
        if self.end_datetime is not None:
            if self.end_datetime < self.start_datetime:
                raise TypeError, 'end datetime before start datetime'

    def set_recurrence(rrule_data):
        """ rrule_data can be either a rrule, a rruleset or a string
        reprensenting one or several rrule in iCalendar format
        """
        if isinstance(rule_or_set_or_rulestr, rruleset):
            self.recurrence = rrule_data
        elif isinstance(rule_or_set_or_rulestr, rrule):
            self.recurrence = rruleset()
            self.recurrence.rrule(rrule)
        elif isinstance(rrule_data, str) or isinstance(rrule_data, unicode):
            self.set_recurrence_from_string(rrule_data)
        else:
            raise TypeError, "don't know how to handle provided recurrence infos"
        return self.recurrence

    def set_recurrence_from_string(rrule_data):
        """ rrule_data is a string representing one or several rule in
        iCalendar format
        """
        rrule_temp = rrulestr(rrule_data)
        if isinstance(rrule_temp, rruleset):
            self.recurrence = rrule_temp
        else: # rrule
            self.recurrence = rruleset()
            self.recurrence.rrule(rrule_temp)
        return self.recurrence

    def __repr__(self):
        return "<CalendarDateInterval sdt=%s, edt=%s>" % \
            (repr(self.__start_datetime), repr(self.__end_datetime))

    def __is_all_day(self, sdt, edt):
        return ((0, 0, 0) == (sdt.hour, sdt.minute, sdt.second)
            and (23, 59, 59) == (edt.hour, edt.minute, edt.second))

    def is_all_day(self):
        self.all_day

    def get_unixtimestamp_range():
        """ return the interval boundaries as unix timestamps tuple
        """
        return (datetime_to_unixtimestamp(self.__start_datetime),
            datetime_to_unixtimestamp(self.__end_datetime))

    def get_unixtimestamp_ranges():
        """ return a collection of ranges of all occurrences of
        the event date as unix timestamps tuples
        """
        if hasattr(self, 'recurrence'):
            return [self.get_unixtimestamp_range()]
        duration = self.get_duration
        def get_interval(datetime):
            return (datetime_to_unixtimestamp(datetime),
                datetime_to_unixtimestamp(datetime + duration),)
        return map(get_interval, list(self.recurrence))


class AgendaItem(NewsItem):
    """Base class for agenda items.
    """
    security = ClassSecurityInfo()
    implements(IAgendaItem)
    silvaconf.baseclass()

InitializeClass(AgendaItem)

class AgendaItemVersion(NewsItemVersion):
    """Base class for agenda item versions.
    """

    security = ClassSecurityInfo()

    implements(IAgendaItemVersion)
    silvaconf.baseclass()

    def __init__(self, id):
        AgendaItemVersion.inheritedAttribute('__init__')(self, id)
        self._start_datetime = None
        self._end_datetime = None
        self._location = ''
        self._display_time = True
        self._calendar_date_representation = None

    def get_calendar_date_representation(self):
        cdr = getattr(self, '_calendar_date_representation', None)
        if cdr is not None:
            return cdr
        sdt = getattr(self, '_start_datetime', None)
        edt = getattr(self, '_end_datetime', None)
        if sdt is None:
            sdt = datetime.utcnow()
        else:
            sdt = to_utc_datetime(sdt)
        if edt is not None:
            edt = to_utc_datetime(edt)
        self._calendar_date_representation = \
            CalendarDateRepresentation(start_datetime=sdt, end_datetime=edt)
        return self._calendar_date_representation

    def idx_timestamp_ranges(self):
        return self._calendar_date_representation.get_unixtimestamp_ranges()

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_display_time')
    def set_display_time(self, display_time):
        self._display_time = display_time

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_start_datetime')
    def set_start_datetime(self, value):
        cdr = self.get_calendar_date_representation()
        cdr.set_start_datetime(value)
        ICataloging(self).reindex()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_end_datetime')
    def set_end_datetime(self, value):
        cdr = self.get_calendar_date_representation()
        cdr.set_end_datetime(value)
        ICataloging(self).reindex()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_location')
    def set_location(self, value):
        self._location = value
        ICataloging(self).reindex()

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'display_time')
    def display_time(self):
        """returns True if the time parts of the datetimes should be displayed
        """
        return self._display_time
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'start_datetime')
    def start_datetime(self):
        """Returns the start date/time
        """
        return self.get_calendar_date_representation().start_datetime

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'end_datetime')
    def end_datetime(self):
        """Returns the start date/time
        """
        return self.get_calendar_date_representation().end_datetime

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'idx_end_datetime')
    idx_end_datetime = end_datetime

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'location')
    def location(self):
        """Returns location manual
        """
        return self._location

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Deliver the contents as plain text, for full-text search
        """
        parenttext = AgendaItemVersion.inheritedAttribute('fulltext')(self)
        return "%s %s" % (parenttext, self._location)

InitializeClass(AgendaItemVersion)
