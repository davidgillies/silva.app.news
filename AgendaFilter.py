# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.4 $
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
import OFS
# Silva
from Products.Silva import SilvaPermissions
# misc
from Products.Silva.helpers import add_and_edit

from Filter import Filter, MetaTypeException

class AgendaFilter(Filter):
    """Silva AgendaFilter
    """
    security = ClassSecurityInfo()

    meta_type = "Silva AgendaFilter"

    def __init__(self, id, title):
        AgendaFilter.inheritedAttribute('__init__')(self, id, title)
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_next_items')
    def get_next_items(self, numdays, meta_types=None):
        """Returns published items from now up to a number of days
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
        """Returns non-excluded published items for a particular month
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
                              'backend_get_items_by_date')
    def backend_get_items_by_date(self, month, year, meta_types=None):
        """Returns all published items for a particular month
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

        return result

    def _is_agenda_addable(self, addable_dict):
        return (
            addable_dict.has_key('instance') and
            IAgendaItem.isImplementedByInstancesOf(
            addable_dict['instance']))

    def get_allowed_meta_types(self):
        """Returns a list of allowed meta_types for this filter"""
        # FIXME: This list should be generated instead of hard-coded
        return ['Silva News PlainAgendaItem Version', 'Silva EUR News Event Version', 'Silva EUR News Oration Version', 'Silva EUR News Promotion Version', 'Silva EUR News Valedictory Lecture Version']

InitializeClass(AgendaFilter)

manage_addAgendaFilterForm = PageTemplateFile("www/agendaFilterAdd", globals(),
                                       __name__='manage_addAgendaFilterForm')

def manage_addAgendaFilter(self, id, title, REQUEST=None):
    """Add an AgendaFilter."""
    if not self.is_id_valid(id):
        return
    object = AgendaFilter(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
