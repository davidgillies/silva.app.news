import icalendar
from datetime import date, datetime
from dateutil.rrule import rrule, rruleset
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc, tzlocal
from DateTime import DateTime

local_timezone = tzlocal()
UTC = tzutc()

def utc_datetime(aDateTime_or_datetime, end=False):
    if isinstance(aDateTime_or_datetime, datetime):
        return datetime_with_timezone(aDateTime_or_datetime).astimezone(UTC)
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
        return aDateTime_or_datetime.utcdatetime().replace(tzinfo=UTC)

def datetime_with_timezone(dt, tz=local_timezone):
    new_dt = dt
    if dt.tzinfo is None:
        new_dt = dt.replace(tzinfo=tz)
    return new_dt

def utc_datetime_to_unixtimestamp(dt):
    """ Workaround a bug in python : unix time is wrong if not in the local
    timezone
    """
    return int(datetime_with_timezone(dt).astimezone(local_timezone).\
        strftime("%s"))

def end_of_day(dt):
    return dt.replace(hour=24, minute=0, second=0)

def start_of_day(dt):
    return dt.replace(hour=0, minute=0, second=0)


class CalendarDateRepresentation(object):

    default_duration = relativedelta(hours=+1)

    def __init__(self, start_datetime,
            end_datetime=None, all_day=False, recurrence=None):

        utc_start_datetime = utc_datetime(start_datetime)
        utc_end_datetime = end_datetime and \
            utc_datetime(end_datetime, end=True)

        self.all_day = all_day

        if self.all_day:
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
        self.start_datetime = utc_datetime(value)
        self.validate()
        return self.start_datetime

    def set_end_datetime(self, value):
        self.end_datetime = utc_datetime(value)
        self.validate()
        return self.end_datetime

    def validate(self):
        if self.start_datetime is None:
            raise TypeError, 'start datetime can\'t be None'
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
            (repr(self.start_datetime), repr(self.end_datetime))

    def is_all_day(self):
        self.all_day

    def get_unixtimestamp_range(self):
        """ return the interval boundaries as unix timestamps tuple
        """
        return (utc_datetime_to_unixtimestamp(self.start_datetime),
            utc_datetime_to_unixtimestamp(self.end_datetime))

    def get_unixtimestamp_ranges(self):
        """ return a collection of ranges of all occurrences of
        the event date as unix timestamps tuples
        """
        if hasattr(self, 'recurrence'):
            return [self.get_unixtimestamp_range()]
        duration = self.get_duration
        def get_interval(datetime):
            return (utc_datetime_to_unixtimestamp(datetime),
                utc_datetime_to_unixtimestamp(datetime + duration),)
        return map(get_interval, list(self.recurrence))
