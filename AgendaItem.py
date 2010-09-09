# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.21 $
import pytz

from zope.interface import implements
from zope.component import getAdapter
from zope.traversing.browser import absoluteURL
from five import grok

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass # Zope 2.12

# Silva interfaces
from Products.SilvaNews.interfaces import IAgendaItem, IAgendaItemVersion
from Products.SilvaNews.interfaces import INewsViewer
from Acquisition import aq_parent

# Silva
from silva.core import conf as silvaconf
from Products.Silva import SilvaPermissions

# SilvaNews
from Products.SilvaNews.NewsItem import NewsItemView
from Products.SilvaNews.NewsItem import NewsItem, NewsItemVersion
from Products.SilvaNews.datetimeutils import (datetime_with_timezone,
    CalendarDatetime, datetime_to_unixtimestamp, get_timezone)
from icalendar.interfaces import IEvent
from icalendar import Calendar

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

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_timezone_name')
    def set_timezone_name(self, name):
        self._timezone_name = name
        self._timezone = get_timezone(name)
        if self._start_datetime:
            self._start_datetime.replace(tzinfo=self._timezone)
        if self._end_datetime:
            self._end_datetime.replace(tzinfo=self._timezone)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_timezone_name')
    def get_timezone_name(self):
        return getattr(self, '_timezone_name',
                       self.service_news.get_timezone())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_timezone')
    def get_timezone(self):
        return getattr(self, '_timezone',
                       self.service_news.get_timezone())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_calendar_datetime')
    def get_calendar_datetime(self):
        if not self._start_datetime:
            return None
        return CalendarDatetime(self._start_datetime, self._end_datetime)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_display_time')
    def set_display_time(self, display_time):
        self._display_time = display_time

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_start_datetime')
    def set_start_datetime(self, value):
        self._start_datetime = datetime_with_timezone(
            value, self.get_timezone())

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_end_datetime')
    def set_end_datetime(self, value):
        self._end_datetime = datetime_with_timezone(
            value, self.get_timezone())

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_location')
    def set_location(self, value):
        self._location = value

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'display_time')
    def display_time(self):
        """returns True if the time parts of the datetimes should be displayed
        """
        return self._display_time

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_start_datetime')
    def get_start_datetime(self, tz=None):
        """Returns the start date/time
        """
        cd = self.get_calendar_datetime()
        if cd:
            return cd.get_start_datetime(tz)
        return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_end_datetime')
    def get_end_datetime(self, tz=None):
        """Returns the start date/time
        """
        cd = self.get_calendar_datetime()
        if cd:
            return cd.get_end_datetime(tz)
        return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_location')
    def get_location(self):
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sort_index')
    def sort_index(self):
        return datetime_to_unixtimestamp(self.get_start_datetime())

    # indexes

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'idx_timestamp_ranges')
    def idx_timestamp_ranges(self):
        return self.get_calendar_datetime().\
            get_unixtimestamp_ranges()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'idx_start_datetime')
    idx_start_datetime = get_start_datetime

InitializeClass(AgendaItemVersion)

class AgendaViewMixin(object):
    def event_img_url(self):
        return '%s/++resource++Products.SilvaNews.browser/date.png' % \
            absoluteURL(self.context, self.request)

    def event_url(self):
        return "%s/event.ics" % absoluteURL(self.context, self.request)


class AgendaItemView(NewsItemView, AgendaViewMixin):
    grok.context(IAgendaItem)
    template = grok.PageTemplate(filename='templates/AgendaItem/index.pt')


class AgendaListItemView(grok.View, AgendaViewMixin):
    """ Render as a list items (search results)
    """

    grok.context(IAgendaItemVersion)
    grok.name('search_result')
    template = grok.PageTemplate(
        filename='templates/AgendaItem/search_result.pt')


class AgendaItemICS(grok.View):
    """ render an ics event
    """
    grok.context(IAgendaItem)
    grok.name('event.ics')

    def update(self):
        self.viewer = None
        parent = aq_parent(self.context)
        if INewsViewer.providedBy(parent):
            self.viewer = parent
        self.request.response.setHeader('Content-Type', 'text/calendar')
        self.content = self.context.get_viewable()
        self.event_factory = getAdapter(self.content, IEvent)

    def render(self):
        cal = Calendar()
        cal.add('prodid', '-//Silva News Calendaring//lonely event//')
        cal.add('version', '2.0')
        cal.add_component(self.event_factory(self.viewer, self.request))
        return unicode(cal)
