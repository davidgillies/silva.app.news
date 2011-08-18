# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$

from datetime import datetime
import logging

from five import grok
from zope import schema
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.intid.interfaces import IIntIds

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem

from Products.Silva import SilvaPermissions
from Products.Silva.Publishable import NonPublishable
from silva.core.references.reference import ReferenceSet
from silva.core.services.interfaces import ICataloging

from silva.app.news.interfaces import INewsItemFilter, IServiceNews
from silva.app.news.interfaces import news_source
from silva.app.news.NewsCategorization import NewsCategorization
from silva.app.news.NewsCategorization import INewsCategorizationSchema
from silva.app.news import datetimeutils
from silva.app.news.datetimeutils import local_timezone

_ = MessageFactory('silva_news')

logger = logging.getLogger('silva.app.news.filter')


class NewsItemFilter(NonPublishable, NewsCategorization, SimpleItem):
    """Super-class for news item filters.

    A NewsItemFilter picks up news from news sources. Editors can
    browse through this news. It can also be used by
    public pages to expose published news items to end users.

    A super-class for the News Filters (NewsFilter, AgendaFilter)
    which contains shared code for both filters"""

    grok.implements(INewsItemFilter)
    grok.baseclass()
    security = ClassSecurityInfo()

    _source_reference_name = 'filter-source'

    def __init__(self, id):
        super(NewsItemFilter, self).__init__(id)
        self._keep_to_path = 0
        self._excluded_items = set()

    # ACCESSORS
    def _get_sources_reference_set(self):
        if hasattr(self, '_v_source_reference_set'):
            refset = getattr(self, '_v_source_reference_set', None)
            if refset is not None:
                return refset
        self._v_source_reference_set = ReferenceSet(self, 'sources')
        return self._v_source_reference_set

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_sources')
    def get_sources(self):
        return list(self._get_sources_reference_set())

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'has_sources')
    def has_sources(self):
        for filter in self._get_sources_reference_set().get_references():
            # We have at least one item in the generator (don't need
            # to consume it all).
            return True
        return False

    def _get_sources_path(self):
        return map(lambda s: s.getPhysicalPath(), self.get_sources())

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'keep_to_path')
    def keep_to_path(self):
        """Returns true if the item should keep to path
        """
        return self._keep_to_path

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_sources')
    def set_sources(self, sources):
        refset = self._get_sources_reference_set()
        refset.set(sources)
        return sources

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'add_source')
    def add_source(self, source):
        refset = self._get_sources_reference_set()
        refset.add(source)
        return source

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'add_excluded_item')
    def add_excluded_item(self, target):
        """Adds or removes an item to or from the excluded_items list
        """
        intid = target
        if not isinstance(intid, int):
            intid = getUtility(IIntIds).register(target)
        self._p_changed = 1
        self._excluded_items.add(intid)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'remove_excluded_item')
    def remove_excluded_item(self, target):
        intid = target
        if not isinstance(intid, int):
            intid = getUtility(IIntIds).register(target)
        self._p_changed = 1
        self._excluded_items.remove(intid)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'remove_excluded_item')
    def set_excluded_item(self, excluded_set):
        self._excluded_items = set(excluded_set)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_excluded_item')
    def is_excluded_item(self, target):
        intid = target
        if not isinstance(intid, int):
            intid = getUtility(IIntIds).register(target)
        return intid in self._excluded_items

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_excluded_items')
    def get_excluded_items(self):
        """Returns a list of object-paths of all excluded items
        """
        return self._excluded_items

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_keep_to_path')
    def set_keep_to_path(self, value):
        """
        Sets the keep_to_path property to restrict the searcharea of
        the browser
        """
        # make sure the var will contain either 0 or 1
        self._keep_to_path = not not value
        ICataloging(self).reindex()

    # HELPERS

    def _collect_subjects(self, service):
        result = set()
        for sub in self._subjects:
            node = service._subjects.find(sub)
            if node is not None:
                result = result.union(set(node.get_subtree_ids()))
        return list(result)

    def _collect_target_audiences(self, service):
        result = set()
        for sub in self._target_audiences:
            node = service._target_audiences.find(sub)
            if node is not None:
                result = result.union(set(node.get_subtree_ids()))
        return list(result)

    def _prepare_query(self, meta_types=None, public_only=True):
        """private method preparing the common fields for a catalog query.

        Return: dict holding the query parameters
        """
        query = {}
        query['path'] = map(lambda s: "/".join(s), self._get_sources_path())
        if public_only:
            query['publication_status'] = 'public'
        service = getUtility(IServiceNews)
        query['subjects'] = {
            'query': self._collect_subjects(service),
            'operator': 'or'}
        query['target_audiences'] = {
            'query': self._collect_target_audiences(service),
            'operator': 'or'}
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        query['meta_type'] = meta_types
        query['sort_on'] = 'display_datetime'
        query['sort_order'] = 'descending'
        return query

    def _query(self, query):
        logger.info('query %s', repr(query))
        return self.service_catalog(query)

    def _query_items(self, query, filter_items=True, max_items=None):
        count = 0
        if filter_items:
            get_id = getUtility(IIntIds).register
        elif max_items is not None:
            # Local catalog optimization
            query['sort_limit'] = max_items

        for brain in self._query(query):
            if max_items is not None and count > max_items:
                break
            item = brain.getObject()
            if filter_items:
                if get_id(item) in self._excluded_items:
                    continue
            count += 1
            yield item

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'filtered_subject_form_tree')
    def filtered_subject_form_tree(self):
        """return a subject_form_tree (for the SMI edit screen)
        that is filtered through a news category filter, or if
        none are found, all subjects from the news service"""
        audject = self.superValues('Silva News Category Filter')
        if audject:
            audject = audject[0].get_subjects()
        service_news = getUtility(IServiceNews)
        return service_news.subject_form_tree(audject)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'filtered_ta_form_tree')
    def filtered_ta_form_tree(self):
        """return a ta_form_tree (for the SMI edit screen)
        that is filtered through a news category filter, or if
        none are found, all ta's from the news service"""
        audject = self.superValues('Silva News Category Filter')
        if audject:
            audject = audject[0].target_audiences()
        service_news = getUtility(IServiceNews)
        return service_news.target_audience_form_tree(audject)


    # refactorized functions
    # these functions where used/copied in both AgendaFilter and NewsFilter,
    # so place here with clear notes on usage

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'search_items')
    def search_items(self, keywords, meta_types=None):
        """Returns the items from the catalog that have keywords in fulltext.
        """
        keywords = unicode(keywords, 'UTF-8')
        if not meta_types:
            meta_types = self.get_allowed_meta_types()

        # replace +'es with spaces so the effect is the same...
        keywords = keywords.replace('+', ' ')
        query = self._prepare_query(meta_types=meta_types)
        query['fulltext'] = keywords.split(' ')
        return self._query_items(query)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_next_items')
    def get_next_items(self, numdays, meta_types=None):
        """ Note: ONLY called by AgendaViewers
        Returns the next <number> AGENDAitems,
        should return items that conform to the
        AgendaItem-interface (IAgendaItemVersion), although it will in
        any way because it requres start_datetime to be set.
        NewsViewers use only get_last_items.
        """
        if not self.has_sources():
            return []

        lastnight = (DateTime()-1).latestTime()
        endate = (lastnight + numdays).latestTime()

        return self._get_items_by_date_range(
            datetimeutils.utc_datetime(lastnight),
            datetimeutils.utc_datetime(endate),
            meta_types)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_last_items')
    def get_last_items(self, number, number_is_days=0, meta_types=None):
        """Returns the last (number) published items
           This is _only_ used by News Viewers.
        """
        if not self.has_sources():
            return []

        query = self._prepare_query(meta_types)
        max_items = None

        if number_is_days:
            # the number specified must be used to restrict
            # the on number of days instead of the number of items
            now = DateTime()
            last_night = now.earliestTime()
            query['display_datetime'] = {
                'query': [last_night - number, now],
                'range': 'minmax'}
        else:
            max_items = number

        return self._query_items(query, max_items=max_items)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_items_by_date')
    def get_items_by_date(
        self, month, year, timezone=local_timezone, meta_types=None):

        if not self.has_sources():
            return []

        return self._get_items_by_date(
                month, year, timezone=timezone, meta_types=meta_types)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_items_by_date_range')
    def get_items_by_date_range(self, start, end, meta_types=None):
        if not self.has_sources():
            return []

        return self._get_items_by_date_range(start, end, meta_types=meta_types)

    def _get_items_by_date(
        self, month, year, timezone=local_timezone, meta_types=None,
        public_only=True, filter_items=True):
        """ This does not play well with recurrence, this should not be used
        with agenda items
        """

        month = int(month)
        year = int(year)
        startdate = datetimeutils.start_of_month(
            datetime(year, month, 1, tzinfo=timezone))
        enddate = datetimeutils.end_of_month(startdate)
        return self._get_items_by_date_range(startdate, enddate,
            meta_types=meta_types, public_only=public_only,
            filter_items=filter_items)

    def _get_items_by_date_range(
        self, start, end, meta_types=None, public_only=True, filter_items=True):

        query = self._prepare_query(meta_types, public_only=public_only)
        query['timestamp_ranges'] = {
            'query': [
                datetimeutils.datetime_to_unixtimestamp(start),
                datetimeutils.datetime_to_unixtimestamp(end)]}

        return self._query_items(query, filter_items=filter_items)


InitializeClass(NewsItemFilter)


class INewsItemFilterSchema(INewsCategorizationSchema):
    sources = schema.Set(
        value_type=schema.Choice(source=news_source),
        title=_(u"sources"),
        description=_(u"Use predefined sources."))
    _keep_to_path = schema.Bool(
        title=_(u"stick to path"))


