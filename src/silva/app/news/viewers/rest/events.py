from datetime import datetime

from five import grok
from infrae import rest
from zope import component
from zope.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL

from silva.app.news.interfaces import IAgendaViewer
from silva.app.news.datetimeutils import UTC


class Events(rest.REST):
    """ JSON interface to agenda events
    """
    grok.context(IAgendaViewer)
    grok.require('zope2.View')
    grok.name('silva.app.news.events')

    def datetime_from_timestamp(self, ts):
        ts = int(ts)
        dt = datetime.fromtimestamp(ts)
        dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(self.timezone)

    def get_events(self, start, end):
        for r in self.context.get_items_by_date_range(start, end):
            version = r.get_viewable()
            if version is not None:
                yield version

    def get_events_occurrences(self, start, end):
        intids = component.getUtility(IIntIds)
        for event in self.get_events(start, end):
            cal_datetime = event.get_calendar_datetime()
            ranges = cal_datetime.get_unixtimestamp_ranges(
                after=start, before=end)
            title = event.get_title()
            url = absoluteURL(event, self.request)
            all_day = event.is_all_day()
            id = "agenda-item-" + str(intids.register(event))
            for start_timestamp, end_timestamp in ranges:
                yield {'title'      : title,
                       'start'      : start_timestamp,
                       'end'        : end_timestamp,
                       'url'        : url,
                       'allDay'     : all_day,
                       'className'  : 'fullcalendar-agenda-item',
                       'id'         : id }

    def GET(self, **kw):
        self.timezone = self.context.get_timezone()
        try:
            start = self.datetime_from_timestamp(
                self.request.get('start'))
            end = self.datetime_from_timestamp(
                self.request.get('end'))
        except (TypeError, ValueError):
            return self.json_response([])
        else:
            return self.json_response(
                list(self.get_events_occurrences(start, end)))
