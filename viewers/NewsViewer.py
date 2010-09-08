# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.34 $

from logging import getLogger

from five import grok
from zope.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.traversing.browser import absoluteURL

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from zExceptions import NotFound

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Content import Content
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from zeam.form import silva as silvaforms
from silva.core.services.interfaces import ICatalogService

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('silva_news')

# SilvaNews
from Products.SilvaNews.interfaces import (INewsViewer, INewsItemVersion,
    show_source, timezone_source, week_days_source, filters_source)
from Products.SilvaNews.ServiceNews import TimezoneMixin

logger = getLogger('Products.SilvaNews.NewsViewer')


class NewsViewer(Content, SimpleItem, TimezoneMixin):
    """Used to show news items on a Silva site.

    When setting up a newsviewer you can choose which news- or
    agendafilters it should use to retrieve the items, and how far
    back in time it should go. The items will then be automatically
    fetched via the filter for each page request.
    """

    meta_type = 'Silva News Viewer'
    grok.implements(INewsViewer)
    silvaconf.icon("www/news_viewer.png")
    silvaconf.priority(3.1)

    security = ClassSecurityInfo()

    def __init__(self, id):
        super(NewsViewer, self).__init__(id)
        self._number_to_show = 25
        self._number_to_show_archive = 10
        self._number_is_days = 0
        self._year_range = 2
        self._filters = []

    def url_for_item(self, obj, request):
        intids = getUtility(IIntIds)
        if INewsItemVersion.providedBy(obj):
            obj = obj.object()
        id = intids.register(obj)
        return "%s/++items++%d" % (absoluteURL(self, request), id,)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'default_timezone')
    def default_timezone(self):
        """ this is an override of TimezoneMixin to make the service news
        to decide the default timezone
        """
        return self.service_news.get_timezone()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'default_timezone_name')
    def default_timezone_name(self):
        return self.service_news.get_timezone_name()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_first_weekday')
    def get_first_weekday(self):
        return getattr(self,
            '_first_weekday',
            self.service_news.get_first_weekday())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'year_range')
    def year_range(self):
        """Returns number of items to show
        """
        if not hasattr(self, '_year_range'):
            self._year_range = 2
        return self._year_range

    get_year_range = year_range

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'number_to_show')
    def number_to_show(self):
        """Returns number of items to show
        """
        return self._number_to_show

    get_number_to_show = number_to_show

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'number_to_show_archive')
    def number_to_show_archive(self):
        """returns the number of items to show per page in the archive"""
        return self._number_to_show_archive

    get_number_to_show_archive = number_to_show_archive

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_published')
    def is_published(self):
        """Returns 1 so the object will be shown in TOCs and such"""
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_deletable')
    def is_deletable(self):
        """return 1 so this object can always be deleted"""
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'can_set_title')
    def can_set_title(self):
        """return 1 so the title can be set"""
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'number_is_days')
    def number_is_days(self):
        """
        Returns the value of number_is_days (which controls whether
        the filter should show <n> items or items of <n> days back)
        """
        return self._number_is_days

    get_number_is_days = number_is_days

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'filters')
    def filters(self):
        """Returns a list of (the path to) all filters of this object
        """
        self.verify_filters()
        return self._filters

    get_filters = filters

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'findfilters')
    def findfilters(self):
        """Returns a list of paths to all filters
        """
        # Happened through searching in the catalog,
        # but must happen through aquisition now...
        #query = {'meta_type': 'Silva NewsFilter',
        # 'path': '/'.join(self.aq_inner.aq_parent.getPhysicalPath())}
        #results = self.service_catalog(query)
        filters = [str(pair[1]) for pair in self.findfilters_pairs()]
        return filters

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_all_filters')
    def get_all_filters(self):
        util = getUtility(ICatalogService)
        query = {}
        query['meta_type'] = {
            'operator': 'or',
            'query': ['Silva News Filter',
                      'Silva Agenda Filter']}
        return [brain.getObject() for brain in util(query)]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'findfilters_pairs')
    def findfilters_pairs(self):
        """Returns a list of tuples (title (path), path) for all filters
        from catalog for rendering formulator-items
        """
        # IS THIS THE MOST EFFICIENT WAY?
        pairs = []
        obj = self.aq_inner
        for item in obj.superValues(['Silva News Filter',
                                  'Silva Agenda Filter']):
            joinedpath = '/'.join(item.getPhysicalPath())
            pairs.append(('%s (<a href="%s/edit">%s</a>)' %
                          (item.get_title(), joinedpath, joinedpath),
                          joinedpath))
        return pairs

    def verify_filters(self):
        allowed_filters = self.findfilters()
        for newsfilter in self._filters:
            if newsfilter not in allowed_filters:
                self._filters.remove(newsfilter)
                self._p_changed = 1

    def _get_items_helper(self, func, sortattr=None):
        #1) helper function for get_items...this was the same
        #code in NV and AV.  Now this helper contains that code
        #and calls func(obj) for each filter to actually
        #get the items.  Func can be a simple lamba: function
        #2) sortattr is an attribute of the CatalogBraings objects
        #   i.e. a result item.  It's a catalog metadata column
        #   use it for fast sort / merging of multiple filters
        #   e.g. on display_datetime or start_datetime
        self.verify_filters()
        results = []
        for newsfilter in self._filters:
            obj = self.aq_inner.restrictedTraverse(newsfilter)
            res = func(obj)
            results += res

        results = self._remove_doubles(results)

        if sortattr:
            results = [(getattr(r,sortattr,None),
                        getattr(r,'object_path',None),r) for r in results ]
            results.sort()
            results = [ r[2] for r in results ]
            results.reverse()
        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items')
    def get_items(self):
        """Gets the items from the filters
        """
        func = lambda x: x.get_last_items(self._number_to_show,
                                          self._number_is_days)
        #merge/sort results if > 1 filter
        sortattr = None
        if len(self._filters) > 1:
            sortattr = 'sort_index'
        results = self._get_items_helper(func,sortattr)
        if not self._number_is_days:
            return results[:self._number_to_show]

        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items_by_date')
    def get_items_by_date(self, month, year):
        """Gets the items from the filters
        """
        func = lambda x: x.get_items_by_date(month,year,
            timezone=self.get_timezone())
        sortattr = None
        if len(self._filters) > 1:
            sortattr = 'sort_index'
        return self._get_items_helper(func,sortattr)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items_by_date_range')
    def get_items_by_date_range(self, start, end):
        """Gets the items from the filters
        """
        func = lambda x: x.get_items_by_date_range(start, end)
        sortattr = None
        if len(self._filters) > 1:
            sortattr = 'sort_index'
        return self._get_items_helper(func,sortattr)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'search_items')
    def search_items(self, keywords):
        """Search the items in the filters
        """
        func = lambda x: x.search_items(keywords)
        sortattr = None
        if len(self._filters) > 1:
            sortattr = 'sort_index'
        return self._get_items_helper(func,sortattr)

    def _remove_doubles(self, resultlist):
        """Removes double items from a resultset from a ZCatalog-query
        (useful when the resultset is built out of more than 1 query)
        """
        retval = []
        paths = []
        for item in resultlist:
            if not item.getPath() in paths:
                paths.append(item.getPath())
                retval.append(item)
        return retval

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'year_in_range_trigger')
    def year_in_range_trigger(self, year):
        """only years within self._year_range are allowed,
        so raise notfound if the year requested is
        outside of this range.
        """
        if not self.year_in_range(year):
            raise NotFound()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'year_in_range')
    def year_in_range(self, year):
        """only years within self._year_range are allowed,
        return true if year is in range
        """
        return abs(year - DateTime().year()) < self.year_range()

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_year_range')
    def set_year_range(self, number):
        """Sets the range of years to show links to
        """
        self._year_range = number

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_number_to_show')
    def set_number_to_show(self, number):
        """Sets the number of items to show
        """
        self._number_to_show = number

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'set_number_to_show_archive')
    def set_number_to_show_archive(self, number):
        """set self._number_to_show_archive"""
        self._number_to_show_archive = number

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_number_is_days')
    def set_number_is_days(self, onoff):
        """Sets the number of items to show
        """
        self._number_is_days = int(onoff)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_filter')
    def set_filters(self, filters):
        """update filters (path to)
        """
        self.verify_filters()
        self._filters = filters


InitializeClass(NewsViewer)


from zope import schema
from zope.interface import Interface


class INewsViewerSchema(Interface):
    """ Fields description for use in forms only
    """
    number_is_days = schema.Choice(
        source=show_source,
        title=_(u"show"),
        description=_(u"Show a specific number of items, or show "
                      u"items from a range of days in the past."),
        required=True)

    number_to_show = schema.Int(
        title=_(u"days / items number"),
        description=_(u"Number of news items to show per page."),
        required=True)

    number_to_show_archive = schema.Int(
        title=_(u"archive number"),
        description=_(u"Number of archive items to show per page."),
        required=True)

    year_range = schema.Int(
        title=_(u"year range"),
        description=_(u"Allow navigation this number of years ahead "
                      u"of / behind today."),
        required=True)

    timezone_name = schema.Choice(
        source=timezone_source,
        title=_(u"timezone"),
        description=_(u"Defines the time zone for the agenda and news "
                      u"items that will be rendered by this viewer."),
        required=True)

    first_week_day = schema.Choice(
        title=_(u"first day of the week"),
        source=week_days_source,
        description=_(u"Define first day of the week for calendar display."),
        required=True)

    filters = schema.Set(
        value_type=schema.Choice(source=filters_source),
        title=_(u"filters"),
        description=_(u"Use predefined filters."))


class NewsViewerAddForm(silvaforms.SMIAddForm):
    """Add form news viewer
    """
    grok.context(INewsViewer)
    grok.name('Silva News Viewer')


class NewsViewerEditForm(silvaforms.SMIEditForm):
    """ Edit form for news viewer
    """
    grok.context(INewsViewer)
    fields = silvaforms.Fields(INewsViewerSchema)
    fields['number_is_days'].mode = u'radio'


class NewsViewerView(silvaviews.View):
    """ Default view for news viewer
    """
    grok.context(INewsViewer)
    template = grok.PageTemplate(filename='../templates/NewsViewer/index.pt')

    def update(self):
        self.request.timezone = self.context.get_timezone()


class NewsViewerSearchView(silvaviews.Page):
    """ Search view for news viewer
    """
    grok.context(INewsViewer)
    grok.name('search')
    template = grok.PageTemplate(filename='../templates/NewsViewer/search.pt')

    def update(self):
        self.request.timezone = self.context.get_timezone()
        self.query = self.request.get('query', '')
        self.results = []
        try:
            self.results = self.context.search_items(self.query) or []
        except: pass


class NewsViewerArchivesView(silvaviews.Page):
    """ Archives view
    """

    grok.context(INewsViewer)
    grok.name('archives')
    template = grok.PageTemplate(filename='../templates/NewsViewer/archives.pt')

    def update(self):
        self.request.timezone = self.context.get_timezone()

    @property
    def currentmonth(self):
        return DateTime().month()

    @property
    def currentyear(self):
        return DateTime().year()

    def get_months(self):
        return self.context.service_news.get_month_abbrs()

    def previous_url(self):
        url_mask = '/archives?&amp;month=%s&amp;year=%s&amp;offset=%s'
        return url_mask % (self.currentmonth, self.currentyear,
            (self.offset - self.batch_size))

    def next_url(self):
        url_mask = '/archives?&amp;month=%s&amp;year=%s&amp;offset=%s'
        return url_mask % (self.currentmonth, self.currentyear,
            (self.offset + self.batch_size))

    def get_user_role(self):
        user = self.request.AUTHENTICATED_USER
        if user.has_role(['Editor', 'ChiefEditor', 'Manager'], self.context):
            return 'Editor'
        elif user.has_role(['Author'], self.context):
            return 'Author'
        elif user.has_role(['Reader'], self.context):
            return 'Reader'
        else:
            return 'Other'
