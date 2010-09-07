from five import grok
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from icalendar import Calendar, Event, vText, vDatetime, vDate
from icalendar.interfaces import ICalendar, IEvent
from Products.SilvaNews.interfaces import IAgendaItemVersion, IAgendaViewer
from Products.SilvaNews.datetimeutils import UTC
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from zope.interface import Interface
from zope.traversing.browser import absoluteURL


class AgendaFactoryEvent(grok.Adapter):
    grok.context(IAgendaItemVersion)
    grok.implements(IEvent)
    grok.provides(IEvent)

    def __call__(self, viewer, request):
        return AgendaEvent(self.context, request, viewer)


class AgendaEvent(Event):

    def __init__(self, context, request, viewer=None):
        super(AgendaEvent, self).__init__()
        intid = getUtility(IIntIds)
        timezone = viewer and viewer.get_timezone() or context.timezone()
        start_dt = context.start_datetime().astimezone(timezone)
        end_dt = context.end_datetime().astimezone(timezone)
        start_date = date(start_dt.year, start_dt.month, start_dt.day)
        end_date = date(end_dt.year, end_dt.month, end_dt.day)
        if start_date == end_date:
            if start_date:
                self['DTSTART'] = vDatetime(start_dt)
            if end_date:
                self['DTEND'] = vDatetime(end_dt)
        else:
            self['DTSTART'] = vDate(start_date)
            self['DTEND'] = vDate(end_date + relativedelta(days=+1))

#        self['RRULE']

        self['UID'] = "%d@silvanews" % intid.register(context.object())
        if context.location:
            self['LOCATION'] = vText(context.location())
        self['SUMMARY'] = vText(context.get_title())
        if viewer is None:
            self['URL'] = absoluteURL(context.object(), request)
        else:
            self['URL'] = viewer.url_for_item(context, request)


class AgendaCalendar(Calendar, grok.MultiAdapter):
    grok.adapts(IAgendaViewer, Interface)
    grok.implements(ICalendar)
    grok.provides(ICalendar)

    def __init__(self, context, request):
        super(AgendaCalendar, self).__init__()
        self.context = context
        self.request = request
        self['PRODID'] = \
            vText('-//Infrae SilvaNews Calendaring//NONSGML Calendar//EN')
        self['VERSION'] = '2.0'
        self['X-WR-CALNAME'] = self.context.get_title()
        self['X-WR-TIMEZONE'] = self.context.get_timezone_name()
        now = datetime.now(UTC)
        for brain in self.context.get_items_by_date_range(
                now + relativedelta(years=-1), now + relativedelta(years=+1)):
            agenda_item_version = brain.getObject()
            event_factory = AgendaFactoryEvent(agenda_item_version)
            event = event_factory(self.context, self.request)
            if event is not None:
                self.add_component(event)


