from five import grok
from zope.component import queryAdapter, getUtility
from zope.interface import implements
from zope.app.intid.interfaces import IIntIds
from icalendar import Calendar, Event, vText, vDatetime, vDate
from icalendar.interfaces import ICalendar, IEvent
from Products.SilvaNews.interfaces import IAgendaItemVersion, IAgendaFilter
from Products.SilvaNews.datetimeutils import UTC, local_timezone
from datetime import date


def utc_vdatetime(dt):
    dtref = dt
    if dt.tzinfo is None:
        dtref = dt.replace(tzinfo=local_timezone)
    return vDatetime(dtref)


class AgendaEvent(Event, grok.Adapter):
    grok.context(IAgendaItemVersion)
    grok.implements(IEvent)
    grok.provides(IEvent)

    def __init__(self, context):
        super(AgendaEvent, self).__init__()
        self.context = context
        date_rep = self.context.get_calendar_date_representation()
        intid = getUtility(IIntIds)
        start_dt = context.start_datetime().astimezone(local_timezone)
        end_dt = context.end_datetime().astimezone(local_timezone)
        start_date = date(start_dt.year, start_dt.month, start_dt.day)
        end_date = date(end_dt.year, end_dt.month, end_dt.day)
        if start_date == end_date:
            if start_date:
                self['DTSTART'] = utc_vdatetime(start_dt)
            if end_date:
                self['DTEND'] = utc_vdatetime(end_dt)
        else:
            self['DTSTART'] = vDate(start_date)
            self['DTEND'] = vDate(end_date)

#        self['RRULE']

        self['UID'] = "%d@silvanews" % intid.register(context.object())
        if context.location:
            self['LOCATION'] = vText(context.location())
        self['SUMMARY'] = vText(context.get_title())
        self['URL'] = context.object().absolute_url()


class AgendaCalendar(Calendar, grok.Adapter):
    grok.context(IAgendaViewer)
    grok.implements(ICalendar)
    grok.provides(ICalendar)

    def __init__(self, context):
        super(AgendaCalendar, self).__init__()
        self.context = context
        self['PRODID'] = \
            vText('Infrae SilvaNews Calendaring//NONSGML Calendar//EN')
        self['VERSION'] = '2.0'
        for agenda_item in self.context.get_items():
            version = agenda_item.get_viewable()
            if version is not None:
                event = queryAdapter(version, IEvent)
                if event is not None:
                    self.add(event)


