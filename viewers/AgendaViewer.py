# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.17 $

from zope.interface import implements

# Zope
import Products
from AccessControl import ClassSecurityInfo
try:
    from App.class_init import InitializeClass # Zope 2.12
except ImportError:
    from Globals import InitializeClass # Zope < 2.12

# Silva

from silva.core.views import views as silvaviews
from five import grok
import calendar
from datetime import datetime

from silva.core import conf as silvaconf
from Products.Silva import SilvaPermissions

# SilvaNews
from Products.SilvaNews.datetimeutils import datetime_with_timezone
from Products.SilvaNews.interfaces import IAgendaItemVersion, IAgendaViewer
from Products.SilvaNews.viewers.NewsViewer import NewsViewer

class AgendaViewer(NewsViewer):
    """
    Used to show agendaitems on a Silva site. When setting up an
    agendaviewer you can choose which agendafilters it should use to
    get the items from and how long in advance you want the items
    shown. The items will then automatically be retrieved from the
    agendafilter for each request.
    """

    security = ClassSecurityInfo()

    implements(IAgendaViewer)
    silvaconf.icon("www/agenda_viewer.png")
    silvaconf.priority(3.3)

    meta_type = "Silva Agenda Viewer"

    show_in_tocs = 1

    def __init__(self, id):
        AgendaViewer.inheritedAttribute('__init__')(self, id)
        self._days_to_show = 31
        self._number_is_days = True

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'days_to_show')
    def days_to_show(self):
        """Returns number of days to show
        """
        return self._days_to_show

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items')
    def get_items(self):
        """Gets the items from the filters
        """
        func = lambda x: x.get_next_items(self._days_to_show)
        sortattr = None
        if len(self._filters) > 1: 
            sortattr = 'start_datetime'
        return self._get_items_helper(func,sortattr)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items_by_date')
    def get_items_by_date(self, month, year):
        """Gets the items from the filters
        """
        func = lambda x: x.get_agenda_items_by_date(month,year)
        sortattr = None
        if len(self._filters) > 1: 
            sortattr = 'start_datetime'
        results = self._get_items_helper(func,sortattr)
        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'search_items')
    def search_items(self, keywords):
        """Search the items in the filters
        """
        allowed_meta_types = self.get_allowed_meta_types()
        func = lambda x: x.search_items(keywords,allowed_meta_types)
        sortattr = None
        if len(self._filters) > 1: 
            sortattr = 'start_datetime'
        results = self._get_items_helper(func,sortattr)
        return results

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this Viewer"""
        """results are passed to the filters, some of which may be
           news filters -- don't want to return PlainNewsItems"""
        allowed = []
        mts = Products.meta_types
        for mt in mts:
            if (mt.has_key('instance') and
                IAgendaItemVersion.implementedBy(mt['instance'])):
                allowed.append(mt['name'])
        return allowed

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_days_to_show')
    def set_days_to_show(self, number):
        """Sets the number of days to show in the agenda
        """
        self._days_to_show = number

InitializeClass(AgendaViewer)


class HTMLCalendar(calendar.calendar):
    


class AgendaViewerMonthCalendar(silvaviews.Page):

    grok.context(IAgendaViewer)
    grok.name('month_calendar')

    def update(self):
        now = datetime_with_timezone(datetime.now())
        self.calendar = calendar.HTMLCalendar()
        self.month = self.request.get('month', now.month)
        self.year = self.request.get('year', now.year)

    def render(self):
        return self.calendar.formatmonth(self.year, self.month)


class AgendaViewerYearCalendar(silvaviews.Page):

    grok.context(IAgendaViewer)
    grok.name('year_calendar')

    def update(self):
        now = datetime_with_timezone(datetime.now())
        self.calendar = calendar.HTMLCalendar()
        self.year = self.request.get('year', now.year)

    def render(self):
        return self.calendar.formatyear(self.year)


