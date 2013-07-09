# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime, timedelta
from logging import getLogger
import operator

from five import grok
from zope import schema
from zope.component import getUtility, getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Content import Content
from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from silva.core.views import views as silvaviews
from silva.core.references.reference import ReferenceSet
from zeam.form import silva as silvaforms
from zeam.utils import batch


# SilvaNews
from silva.app.news.interfaces import get_default_tz_name, timezone_source
from silva.app.news.interfaces import (INewsViewer, IServiceNews,
    show_source, week_days_source, make_filters_source)
from silva.app.news.ServiceNews import TimezoneMixin


_ = MessageFactory('silva_news')
logger = getLogger('silva.app.news.viewer')


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

    _filter_reference_name = u'viewer-filter'

    _number_to_show = 25
    _number_to_show_archive = 10
    _number_is_days = False

    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'default_timezone')
    def default_timezone(self):
        """ this is an override of TimezoneMixin to make the service news
        to decide the default timezone
        """
        return getUtility(IServiceNews).get_timezone()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'default_timezone_name')
    def default_timezone_name(self):
        return getUtility(IServiceNews).get_timezone_name()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_first_weekday')
    def get_first_weekday(self):
        first_weekday = getattr(self, '_first_weekday', None)
        if first_weekday is None:
            return getUtility(IServiceNews).get_first_weekday()
        return first_weekday

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_number_to_show')
    def get_number_to_show(self):
        """Returns number of items to show
        """
        return self._number_to_show

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_number_to_show_archive')
    def get_number_to_show_archive(self):
        """returns the number of items to show per page in the archive"""
        return self._number_to_show_archive

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_number_is_days')
    def get_number_is_days(self):
        """
        Returns the value of number_is_days (which controls whether
        the filter should show <n> items or items of <n> days back)
        """
        return self._number_is_days

    def _get_filters_reference_set(self):
        if hasattr(self, '_v_filter_reference_set'):
            refset = getattr(self, '_v_filter_reference_set', None)
            if refset is not None:
                return refset
        self._v_filter_reference_set = ReferenceSet(self, 'filters')
        return self._v_filter_reference_set

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_filters')
    def get_filters(self):
        """Returns a list of all filters of this object
        """
        return list(self._get_filters_reference_set())

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'has_filter')
    def has_filter(self):
        """Returns a list of (the path to) all filters of this object
        """
        for filter in self._get_filters_reference_set().get_references():
            # We have at least one item in the generator (don't need
            # to consume it all).
            return True
        return False

    def _get_items(self, generator):
        # 1) helper function for get_items...this was the same
        # code in NV and AV.  Now this helper contains that code
        # and calls func(obj) for each filter to actually
        # get the items.

        seen_ids = set()
        filter_count = 0
        items = []

        for news_filter in self._get_filters_reference_set():
            for item in generator(news_filter):
                # Check for duplicate using content_intid
                if filter_count and item.content_intid in seen_ids:
                    continue
                seen_ids.add(item.content_intid)
                items.append(item)
            filter_count += 1

        if filter_count > 1:
            # Sort only if we have more than one filter used.
            items.sort(key=operator.attrgetter('sort_index'), reverse=True)
        return items

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_items')
    def get_items(self):
        """Gets the items from the filters
        """
        results = self._get_items(lambda x: x.get_last_items(
                self._number_to_show, self._number_is_days))

        if not self._number_is_days:
            return results[:self._number_to_show]

        return results

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_items_by_date')
    def get_items_by_date(self, month, year):
        """Gets the items from the filters
        """
        return self._get_items(lambda x: x.get_items_by_date(
                month,year, timezone=self.get_timezone()))

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_items_by_date_range')
    def get_items_by_date_range(self, start, end):
        """Gets the items from the filters
        """
        return self._get_items(lambda x: x.get_items_by_date_range(start, end))

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'search_items')
    def search_items(self, keywords):
        """Search the items in the filters
        """
        return self._get_items(lambda x: x.search_items(keywords))

    # MANIPULATORS

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_number_to_show')
    def set_number_to_show(self, number):
        """Sets the number of items to show
        """
        self._number_to_show = number

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_number_to_show_archive')
    def set_number_to_show_archive(self, number):
        """set self._number_to_show_archive"""
        self._number_to_show_archive = number

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_number_is_days')
    def set_number_is_days(self, onoff):
        """Sets the number of items to show
        """
        self._number_is_days = bool(onoff)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_filters')
    def set_filters(self, filters):
        """update filters
        """
        self._get_filters_reference_set().set(filters)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'add_filter')
    def add_filter(self, filter):
        """add filters
        """
        self._get_filters_reference_set().add(filter)
        return filter

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'allow_feeds')
    def allow_feeds(self):
        return True


InitializeClass(NewsViewer)


class INewsViewerFields(Interface):
    """ Fields description for use in forms only
    """
    filters = schema.Set(
        value_type=schema.Choice(source=make_filters_source()),
        title=_(u"filters"),
        description=_(u"Use predefined filters."))

    number_is_days = schema.Choice(
        source=show_source,
        title=_(u"show"),
        description=_(u"Show a specific number of items, or show "
                      u"items from a range of days in the past."),
        default=1,
        required=True)

    number_to_show = schema.Int(
        title=_(u"days / items number"),
        description=_(u"Number of news items to show per page."),
        default=25,
        required=True)

    number_to_show_archive = schema.Int(
        title=_(u"archive number"),
        description=_(u"Number of archive items to show per page."),
        default=10,
        required=True)

    timezone_name = schema.Choice(
        source=timezone_source,
        title=_(u"timezone"),
        description=_(u"Defines the time zone for the agenda and news "
                      u"items that will be rendered by this viewer."),
        required=True)

    first_weekday = schema.Choice(
        title=_(u"first day of the week"),
        source=week_days_source,
        description=_(u"Define first day of the week for calendar display."),
        required=True)


class NewsViewerAddForm(silvaforms.SMIAddForm):
    """Add form news viewer
    """
    grok.context(INewsViewer)
    grok.name('Silva News Viewer')

    fields = silvaforms.Fields(ITitledContent, INewsViewerFields)
    fields['number_is_days'].mode = u'radio'
    fields['timezone_name'].defaultValue = get_default_tz_name


class NewsViewerEditForm(silvaforms.SMIEditForm):
    """ Edit form for news viewer
    """
    grok.context(INewsViewer)
    fields = silvaforms.Fields(ITitledContent, INewsViewerFields).omit('id')
    fields['number_is_days'].mode = u'radio'
    fields['timezone_name'].defaultValue = get_default_tz_name


class NewsViewerView(silvaviews.View):
    """ Default view for news viewer
    """
    grok.context(INewsViewer)

    def update(self):
        self.query = self.request.get('query', '')
        if self.query:
            brains = self.context.search_items(self.query)
        else:
            brains = self.context.get_items()
        self.items = map(lambda b: b.getObject().get_content(), brains)


class NewsViewerArchivesView(silvaviews.Page):
    """ Archives view
    """
    grok.context(INewsViewer)
    grok.name('archives.html')

    def update(self):

        def getter(date):
            return self.context.get_items_by_date(date.month, date.year)

        today = datetime.today()
        # Limit the scope of the batch to 5 years in the future, 20 in the past.
        # This should be configurable.
        items = batch.DateBatch(
            getter,
            request=self.request,
            min=today - timedelta(days=20 * 365),
            max=today + timedelta(days=5 * 365))
        self.batch = getMultiAdapter(
            (self, items, self.request), batch.IBatching)()
        self.items = map(lambda b: b.getObject().get_content(), items)

        # Get the month and year of the corresponding periode
        calendar = self.request.locale.dates.calendars['gregorian']
        periode = items.start
        self.periode = '%s %s' % (
            calendar.getMonthNames()[periode.month-1], periode.year)
