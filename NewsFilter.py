# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
import OFS
# Silva
import Products.Silva.SilvaPermissions as SilvaPermissions
# misc
from Products.Silva.helpers import add_and_edit

from Filter import Filter, MetaTypeException

class NewsFilter(Filter):
    """Silva NewsFilter
    """
    security = ClassSecurityInfo()

    meta_type = "Silva NewsFilter"

    def __init__(self, id, title):
        NewsFilter.inheritedAttribute('__init__')(self, id, title)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_all_items')
    def get_all_items(self, meta_types=None):
        """Returns all items available to this filter. This function will probably only
        be used in the back-end, but nevertheless has AccessContentsInformation-security
        because it does not reveal any 'secret' information...
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()
        query = {}
        query['path'] = self._sources
        query['version_status'] = 'public'
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'creation_datetime'
        query['sort_order'] = 'descending'
        results = getattr(self, self._catalog)(query)

        print "Query: %s" % query
        print "Results: %s" % results

        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_last_items')
    def get_last_items(self, number, meta_types=None):
        """Returns the last self._number_to_show published items
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()
        query = {}
        query['path'] = self._sources
        query['version_status'] = 'public'
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'publication_datetime'
        query['sort_order'] = 'descending'
        result = getattr(self, self._catalog)(query)
        filtered_result = [r for r in result if not r.object_path in self._excluded_items]
        output = []
        for i in range(len(filtered_result)):
            if i < number:
                output.append(filtered_result[i])
            else:
                break

        return output

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items_by_date')
    def get_items_by_date(self, month, year, meta_types=None):
        """Returns the last self._number_to_show published items
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()
        month = int(month)
        year = int(year)
        startdate = DateTime(year, month, 1)
        endmonth = month + 1
        if month == 12:
            endmonth = 1
            year = year + 1
        enddate = DateTime(year, endmonth, 1)
        query = {}
        query['publication_datetime'] = (startdate, enddate)
        query['publication_datetime_usage'] = 'range:min:max'
        query['version_status'] = 'public'
        query['path'] = self._sources
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'publication_datetime'
        query['sort_order'] = 'descending'
        result = getattr(self, self._catalog)(query)

        return [r for r in result if not r.object_path in
                self._excluded_items]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'search_items')
    def search_items(self, keywords, meta_types=None):
        """Returns the items from the catalog that have keywords in fulltext
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()

        # replace +'es with spaces so the effect is the same...
        keywords = keywords.replace('+', ' ')

        query = {}
        query['fulltext'] = keywords.split(' ')
        query['version_status'] = 'public'
        query['path'] = self._sources
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'publication_datetime'
        query['sort_order'] = 'descending'
        result = getattr(self, self._catalog)(query)

        return [r for r in result if not r.object_path in
                self._excluded_items]

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this filter"""
        # FIXME: This should be generated instead of hard-coded...
        return ['Silva EUR News Announcement Version', 'Silva EUR News Article Version']

InitializeClass(NewsFilter)

manage_addNewsFilterForm = PageTemplateFile("www/newsFilterAdd", globals(),
                                       __name__='manage_addNewsFilterForm')

def manage_addNewsFilter(self, id, title, REQUEST=None):
    """Add an NewsFilter."""
    if not self.is_id_valid(id):
        return
    object = NewsFilter(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
