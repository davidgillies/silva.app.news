from five import grok
from zope.component import queryAdapter, getUtility
from zope.interface import implements
from zope.app.intid.interfaces import IIntIds
from icalendar import Calendar, Event, vText, vDatetime, UTC, LocalTimezone
from icalendar.interfaces import ICalendar, IEvent
from Products.SilvaNews.interfaces import IAgendaItemVersion, IAgendaFilter

local_timezone = LocalTimezone()

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
        intid = getUtility(IIntIds)
        start_date = context.start_datetime()
        end_date = context.end_datetime()
        if start_date:
            self['DTSTART'] = utc_vdatetime(start_date)
        if end_date:
            self['DTEND'] = utc_vdatetime(end_date)

        self['UID'] = "%d@calendar.silva" % intid.register(context.object())
        if context.location:
            self['LOCATION'] = vText(context.location)
        self['SUMMARY'] = vText(context.get_title())
        self['URL'] = context.object().absolute_url()


# class AgendaCalendar(Calendar, grok.Adapter):
#     grok.context(IAgendaViewer)
#     grok.implements(ICalendar)
#     grok.provides(ICalendar)
# 
#     def __init__(self, context):
#         super(AgendaCalendar, self).__init__()
#         self.context = context
#         self['PRODID'] = \
#             vText('Infrae SilvaNews Calendaring//NONSGML Calendar//EN')
#         self['VERSION'] = vText('1.0')
#         for agenda_item in self.context.get_items():
#             version = agenda_item.get_viewable()
#             if version is not None:
#                 event = queryAdapter(version, IEvent)
#                 if event is not None:
#                     self.add(event)


