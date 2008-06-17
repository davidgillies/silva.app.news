# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.17 $

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DateTime import DateTime

# Silva 
import Products.Silva.SilvaPermissions as SilvaPermissions

# Silva/News interfaces
from interfaces import INewsItem,INewsFilter,INewsItemFilter
from Filter import Filter

class MetaTypeException(Exception):
    pass

def brainsorter(a, b):
    atime = a.start_datetime
    btime = b.start_datetime
    return cmp(atime, btime)

class NewsItemFilter(Filter):
    """Super-class for news item filters.

    A NewsItemFilter picks up news from news sources. Editors can
    browse through this news. It can also be used by
    public pages to expose published news items to end users.

    A super-class for the News Filters (NewsFilter, AgendaFilter)
    which contains shared code for both filters"""

    implements(INewsItemFilter)
    security = ClassSecurityInfo()

    def __init__(self, id):
        NewsItemFilter.inheritedAttribute('__init__')(self, id)
        self._keep_to_path = 0
        self._excluded_items = []
        self._sources = []

    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'find_sources')
    def find_sources(self):
        """Returns all the sources available for querying
        """
        results = self._query(
            meta_type=self._allowed_source_types,
            sort_on='id',
            idx_is_private=0)

        pp = []
        cpp = '/'.join(self.aq_inner.aq_parent.getPhysicalPath())
        while 1:
            if cpp == '':
                break
            pp.append(cpp)
            cpp = cpp[:cpp.rfind('/')]

        results += self._query(
            meta_type=self._allowed_source_types,
            sort_on='id',
            idx_is_private=1,
            idx_parent_path=pp)

        # remove doubles
        res = []
        urls = []
        for r in results:
            if not r.getURL() in urls:
                res.append(r)
                urls.append(r.getURL())

        return res

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sources')
    def sources(self):
        """Returns the list of sources
        """
        self.verify_sources()
        return self._sources

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'keep_to_path')
    def keep_to_path(self):
        """Returns true if the item should keep to path
        """
        return self._keep_to_path

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'add_source')
    def add_source(self, sourcepath, add_or_remove):
        """Add a source
        """
        if add_or_remove:
            if not sourcepath in self._sources:
                self._sources.append(sourcepath)
        else:
            if sourcepath in self._sources:
                self._sources.remove(sourcepath)
        self._p_changed = 1
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'verify_sources')
    def verify_sources(self):
        """Verifies the sourcelist against the available sources
        """
        allowedsources = [s.getPath() for s in self.find_sources()]
        do_reindex = 0
        for source in self._sources:
            if not source in allowedsources:
                self._sources.remove(source)
                do_reindex = 1
        if do_reindex:
            self._p_changed=1
            self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_excluded_item')
    def set_excluded_item(self, objectpath, add_or_remove):
        """Adds or removes an item to or from the excluded_items list
        """
        if add_or_remove:
            if not objectpath in self._excluded_items:
                self._excluded_items.append(objectpath)
        else:
            if objectpath in self._excluded_items:
                self._excluded_items.remove(objectpath)
        self._p_changed = 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'excluded_items')
    def excluded_items(self):
        """Returns a list of object-paths of all excluded items
        """
        self.verify_excluded_items()
        return self._excluded_items

    def verify_excluded_items(self):
        do_reindex = 0
        for item in self._excluded_items:
            result = self._query(object_path=[item])
            if not str(item) in [str(i.object_path) for i in result]:
                self._excluded_items.remove(item)
                do_reindex = 1
        if do_reindex:
            self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_keep_to_path')
    def set_keep_to_path(self, value):
        """
        Sets the keep_to_path property to restrict the searcharea of
        the browser
        """
        # make sure the var will contain either 0 or 1
        self._keep_to_path = not not value
        self.reindex_object()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'search_items')
    def search_items(self, keywords, meta_types=None):
        """Returns the items from the catalog that have keywords in fulltext.
        """
        keywords = unicode(keywords, 'UTF-8')
        self.verify_sources()
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()

        # replace +'es with spaces so the effect is the same...
        keywords = keywords.replace('+', ' ')

        result = self._query(
            fulltext = keywords.split(' '),
            version_status = 'public',
            path = self._sources,
            subjects = self._subjects,
            target_audiences = self._target_audiences,
            meta_type = meta_types,
            sort_on = 'idx_display_datetime',
            sort_order = 'descending')

        result =  [r for r in result if not r.object_path in
                   self._excluded_items]

        return result

    # HELPERS

    def _prepare_query ( self, meta_types=None ):
        """private method preparing the common fields for a catalog query.

        Return: dict holding the query parameters
        """
        self.verify_sources()
        self.verify_excluded_items()
        query = {}
        query['path'] = self._sources
        query['version_status'] = 'public'
        query['idx_subjects'] = {'query': self._subjects,
                                'operator': 'or'}
        query['idx_target_audiences'] = {'query': self._target_audiences,
                                        'operator': 'or'}
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        query['meta_type'] = meta_types
        # Workaround for ProxyIndex bug
        query['sort_on'] = 'idx_display_datetime'
        query['sort_order'] = 'descending'
        return query

    def _query(self, **kw):
        return self.service_catalog(kw)
    
    def _check_meta_types(self, meta_types):
        for type in meta_types:
            if type not in self._allowed_news_meta_types():
                raise MetaTypeException, "Illegal meta_type: %s" % type

    def _allowed_news_meta_types(self):
        return [addable_dict['name']
                for addable_dict in self.filtered_meta_types()
                if self._is_news_addable(addable_dict)]

    def _is_news_addable(self, addable_dict):
        return (
            addable_dict.has_key('instance') and
            INewsItem.isImplementedByInstancesOf(
            addable_dict['instance']))

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'filtered_subject_form_tree')
    def filtered_subject_form_tree(self):
        """return a subject_form_tree (for the SMI edit screen)
        that is filtered through a news category filter, or if
        none are found, all subjects from the news service"""
        audject = self.superValues('Silva News Category Filter')
        if audject:
            audject = audject[0].subjects()
        return self.service_news.subject_form_tree(audject)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'filtered_ta_form_tree')
    def filtered_ta_form_tree(self):
        """return a ta_form_tree (for the SMI edit screen)
        that is filtered through a news category filter, or if
        none are found, all ta's from the news service"""
        audject = self.superValues('Silva News Category Filter')
        if audject:
            audject = audject[0].target_audiences()
        return self.service_news.target_audience_form_tree(audject)


    # refactorized functions
    # these functions where used/copied in both AgendaFilter and NewsFilter,
    # so place here with clear notes on usage

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_next_items')
    def get_next_items(self, numdays, meta_types=None):
        """ Note: ONLY called by AgendaViewers
        Returns the next <number> AGENDAitems,
        should return items that conform to the
        AgendaItem-interface (IAgendaItemVersion), although it will in
        any way because it requres start_datetime to be set.
        NewsViewers use only get_last_items.
        """
        self.verify_sources()
        if not self._sources:
            return []

        result = []

        #if this is a new filter that doesn't show agenda items
        if (INewsFilter.providedBy(self) and not self.show_agenda_items()):
            return result

        lastnight = (DateTime()-1).latestTime()
        #we want the range from 12:00 a.m. to 11:59 p.m.
        if numdays == 1: #get only one day
            enddate = (lastnight+1).latestTime()
        else:
            enddate = (lastnight + 1 + (numdays-1)).latestTime()

        query = self._prepare_query(meta_types)
        query['sort_order'] = 'ascending'

        query['sort_on'] = 'idx_end_datetime'
        query['idx_end_datetime'] = {'query': [lastnight, enddate],
                                     'range': 'minmax' }
        result_enddt = self._query(**query)

        for item in result_enddt:
            if item.object_path not in self._excluded_items:
                result.append(item)

        del query['idx_end_datetime']
        query['idx_start_datetime'] = {'query': [lastnight, enddate],
                                       'range': 'minmax'}
        query['sort_on'] = 'idx_start_datetime'
        result_startdt = self._query(**query)

        # copy only those objects from result_startdt for which an end 
        # datetime is not set (since the ones with an end date/time are 
        # already retrieved above)
        for item in result_startdt:
            #XXX this needs to be updated once end_datetime is in the catalog
            #    there will be no need to get the object here
            edt = item.end_datetime
            if (item.object_path not in self._excluded_items and
                (not edt or edt > enddate)):
                result.append(item)

        #special case where event startime < today, and endtime is > num_days.
        query['idx_start_datetime'] = { 'query':lastnight,
                                        'range':'max'}
        query['idx_end_datetime'] = { 'query': enddate,
                                      'range': 'min'}
        result_middle = self._query(**query)
        for item in result_middle:
            if not item.object_path in self._excluded_items:
                result.append(item)

        result = [r for r in result]
        result.sort(brainsorter)

        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_last_items')
    def get_last_items(self, number, number_is_days=0, meta_types=None):
        """Returns the last (number) published items
           This is _only_ used by News Viewers.
        """
        self.verify_sources()
        if not self._sources:
            return []

        query = self._prepare_query(meta_types)

        if number_is_days:
            # the number specified must be used to restrict the on number of days instead of the number of items
            now = DateTime()
            last_night = now.earliestTime()
            query['idx_display_datetime'] = {'query': [last_night - number, now],
                                             'range': 'minmax'}
        result = self._query(**query)
        filtered_result = [r for r in result if not r.object_path in self._excluded_items]

        if not number_is_days:
            output = filtered_result[:number]
        else:
            output = filtered_result
        return output

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_agenda_items_by_date')
    def get_agenda_items_by_date(self, month, year, meta_types=None):
        """
        Returns non-excluded published AGENDA-items for a particular
        month. This method is for exclusive use by AgendaViewers only,
        NewsViewers should use get_items_by_date instead (which
        filters on idx_display_datetime instead of start_datetime and
        returns all objects instead of only IAgendaItem-
        implementations)
        -- This was in both News and Agenda Filters, with slightly
        different code, so refactored into Filter
        """
        self.verify_sources()
        if not self._sources:
            return []
        
        result = []

        #if this is a new filter that doesn't show agenda items
        if (INewsFilter.providedBy(self) and not self.show_agenda_items()):
            return result

        month = int(month)
        year = int(year)
        startdate = DateTime(year, month, 1).earliestTime()
        endmonth = month + 1
        if month == 12:
            endmonth = 1
            year = year + 1
        enddate = DateTime(year, endmonth, 1).earliestTime()

        result = []
        result_objects = {}

        # first query for objects that do have an end datetime defined
        query = self._prepare_query(meta_types)
        query['idx_end_datetime'] = {'query':[startdate, enddate],
                                     'range':'minmax'}
        query['sort_on'] = 'idx_end_datetime'
        query['sort_order'] = 'ascending'
        result_enddt = self._query(**query)

        for item in result_enddt:
            if item.object_path not in self._excluded_items:
                result.append(item)
                result_objects[item.object_path] = 1
        
        # now those that don't have end_datetime
        del query['idx_end_datetime']
        query['idx_start_datetime'] = {'query':[startdate, enddate],
                                       'range':'minmax'}
        query['sort_on'] = 'idx_start_datetime'
        result_startdt = self._query(**query)

        # remove the items with an end_dt from the result_startdt
        # only add items without an end_dt or with an end_dt in a different month.
        for item in result_startdt:
            edt = item.end_datetime
            if (item.object_path not in self._excluded_items and not result_objects.get(item.object_path,None)):
                if not edt or edt.month()!= month or edt.year() != year:
                    result_objects[item.object_path] = 1
                    result.append(item)

        result = [r for r in result]
        result.sort(brainsorter)

        return result
InitializeClass(NewsItemFilter)
