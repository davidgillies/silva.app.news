# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.21 $

from zope.interface import implements
from zope.component import getAdapter
from five import grok

# Zope
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime

from App.class_init import InitializeClass # Zope 2.12

# Silva interfaces
from Products.SilvaNews.interfaces import IAgendaItem, IAgendaItemVersion
from Products.SilvaNews.interfaces import (INewsItem, INewsItemVersion,
    INewsViewer)
from Acquisition import aq_parent

# Silva
from silva.core import conf as silvaconf
from silva.core.interfaces import IVersionedContent
from silva.core.services.interfaces import ICataloging
from silva.core.views import views as silvaviews

from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit

# SilvaNews
from Products.SilvaNews.NewsItem import NewsItem, NewsItemVersion
from Products.SilvaNews.datetimeutils import (utc_datetime,
    CalendarDateRepresentation, local_timezone)
from datetime import datetime
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
        self._calendar_date_representation = None

    def set_volatile_timezone(self, tz):
        self._v_timezone = tz

    def timezone(self):
        return getattr(self, '_v_timezone', self.service_news.get_timezone())

    def get_calendar_date_representation(self):
        cdr = getattr(self, '_calendar_date_representation', None)
        if cdr is not None:
            return cdr
        sdt = getattr(self, '_start_datetime', None)
        edt = getattr(self, '_end_datetime', None)
        if sdt is None:
            sdt = utc_datetime(datetime.now())
        else:
            sdt = utc_datetime(sdt)
        if edt is not None:
            edt = utc_datetime(edt)
        self._calendar_date_representation = \
            CalendarDateRepresentation(start_datetime=sdt, end_datetime=edt)
        return self._calendar_date_representation

    def idx_timestamp_ranges(self):
        return self.get_calendar_date_representation().get_unixtimestamp_ranges()

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
    def start_datetime(self, tz=None):
        """Returns the start date/time
        """
        return self.get_calendar_date_representation().\
            start_datetime.astimezone(tz or self.timezone())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'end_datetime')
    def end_datetime(self, tz=None):
        """Returns the start date/time
        """
        return self.get_calendar_date_representation().\
            end_datetime.astimezone(tz or self.timezone())

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

from Products.SilvaNews.NewsItem import NewsItemView


class AgendaItemView(NewsItemView):
    grok.context(IAgendaItem)
    template = grok.PageTemplate(filename='templates/AgendaItem/index.pt')

    def event_img_url(self):
        return '%s/++resource++Products.SilvaNews.browser/date.png' % \
            self.context.absolute_url()

    def event_url(self):
        return "%s/event.ics" % self.context.absolute_url()


class AgendaListItemView(grok.View):
    """ Render as a list items (search results)
    """

    grok.context(IAgendaItemVersion)
    grok.name('search_result')
    template = grok.PageTemplate(
        filename='templates/AgendaItem/search_result.pt')

    def event_url(self):
        return "%s/event.ics" % self.context.object().absolute_url()


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
        cal.add_component(self.event_factory(self.viewer))
        return unicode(cal)


