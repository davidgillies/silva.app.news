# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.10 $
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
from INewsItem import INewsItemVersion
from IAgendaItem import IAgendaItemVersion

class NewsFilter(Filter):
    """Silva NewsFilter
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News NewsFilter"

    def __init__(self, id, title):
        NewsFilter.inheritedAttribute('__init__')(self, id, title)
        self._show_agenda_items = 0

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
        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_last_items')
    def get_last_items(self, number, number_is_days=0, meta_types=None):
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
        if number_is_days:
            # the number specified must be used to restrict the on number of days instead of the number of items
            now = DateTime()
            last_night = DateTime(now.strftime("%Y/%m/%d"))
            query['publication_datetime'] = [last_night - number, now]
            query['publication_datetime_usage'] = 'range:min:max'
        query['sort_on'] = 'publication_datetime'
        query['sort_order'] = 'descending'

        result = getattr(self, self._catalog)(query)
        filtered_result = [r for r in result if not r.object_path in self._excluded_items]
        output = []
        if not number_is_days:
            for i in range(len(filtered_result)):
                if i < number:
                    output.append(filtered_result[i])
                else:
                    break
        else:
            output = filtered_result

        return output

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_next_items')
    def get_next_items(self, numdays, meta_types=None):
        """Returns the next <number> AGENDAitems, called by AgendaViewer only and should return items
        that conform to the AgendaItem-interface (IAgendaItemVersion), although it will in any way because it
        requres start_datetime to be set. The NewsViewer uses only get_last_items.
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()
        date = DateTime()
        lastnight = DateTime(date.year(), date.month(), date.day(), 0, 0, 0)
        enddate = lastnight + numdays
        query = {}
        query['start_datetime'] = (lastnight, enddate)
        query['start_datetime_usage'] = 'range:min:max'
        query['version_status'] = 'public'
        query['path'] = self._sources
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'start_datetime'
        query['sort_order'] = 'descending'
        result = getattr(self, self._catalog)(query)

        return [r for r in result if not r.object_path in self._excluded_items]

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
                              'get_agenda_items_by_date')
    def get_agenda_items_by_date(self, month, year, meta_types=None):
        """Returns non-excluded published AGENDA-items for a particular month. This method is for
        exclusive use by AgendaViewers only, NewsViewers should use get_items_by_date instead (which filters
        on publication_datetime instead of start_datetime and returns all objects instead of only IAgendaItem-
        implementations)
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
        query['start_datetime'] = [startdate, enddate]
        query['start_datetime_usage'] = 'range:min:max'
        query['version_status'] = 'public'
        query['path'] = self._sources
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'start_datetime'
        query['sort_order'] = 'descending'
        result = getattr(self, self._catalog)(query)

        return [r for r in result if not r.object_path in self._excluded_items]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'show_agenda_items')
    def show_agenda_items(self):
        return self._show_agenda_items

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_show_agenda_items')
    def set_show_agenda_items(self, value):
        self._show_agenda_items = not not int(value)

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this filter"""
        allowed = []
        mts = self.filtered_meta_types()
        for mt in mts:
            if mt.has_key('instance'):
                if INewsItemVersion.isImplementedByInstancesOf(mt['instance']):
                    allowed.append(mt['name'])
                elif self._show_agenda_items:
                    if IAgendaItemVersion.isImplementedByInstancesOf(mt['instance']):
                        allowed.append(mt['name'])
        return allowed

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
