# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.6 $

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS import Folder

from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva.IContent import IContent

from NewsViewer import NewsViewer

class AgendaViewer(NewsViewer):
    """Silva AgendaViewer
    """

    security = ClassSecurityInfo()

    __implements__ = IContent

    meta_type = "Silva News AgendaViewer"

    def __init__(self, id, title):
        AgendaViewer.inheritedAttribute('__init__')(self, id, title)
        self._days_to_show = 31
        self._filters = []

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'findfilters_pairs')
    def findfilters_pairs(self):
        """Returns a list of tuples (title, path) for all filters
        from catalog for rendering formulator-items
        """
        # IS THIS THE MOST EFFICIENT WAY?
        pairs = []
        obj = self.aq_inner
        while 1:
            parent = obj.aq_parent
            parentpath = parent.getPhysicalPath()
            for item in parent.objectValues(['Silva AgendaFilter', 'Silva NewsFilter']):
                joinedpath = '/'.join(parentpath)
                pairs.append(('%s (%s)' % (item.get_title_html(), joinedpath), "%s/%s" % (joinedpath, item.id)))
            if parentpath == ('',):
                break
            obj = parent

        return pairs

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
        results = []
        for newsfilter in self._filters:
            obj = self.aq_inner.restrictedTraverse(newsfilter)
            res = obj.get_next_items(self._days_to_show)
            results += res

        results = self._remove_doubles(results)
        results.sort(self._sortresults)
        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items_by_date')
    def get_items_by_date(self, month, year):
        """Gets the items from the filters
        """
        results = []
        for newsfilter in self._filters:
            obj = self.aq_inner.restrictedTraverse(newsfilter)
            res = obj.get_agenda_items_by_date(month, year)
            results += res

        results = self._remove_doubles(results)
        results.sort(self._sortresults)
        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'search_items')
    def search_items(self, keywords):
        """Search the items in the filters
        """
        self.verify_filters()
        results = []
        for newsfilter in self._filters:
            obj = self.aq_inner.restrictedTraverse(newsfilter)
            res = obj.search_items(keywords)
            results += res

        results = self._remove_doubles(results)
        results.sort(self._sortresults)
        if not self._number_is_days:
            return results[:self._number_to_show]
        else:
            return results

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_days_to_show')
    def set_days_to_show(self, number):
        """Sets the number of days to show in the agenda
        """
        self._days_to_show = number
        self._p_changed = 1

    def _sortresults(self, item1, item2):
        return cmp(item1.start_datetime, item2.start_datetime)

InitializeClass(AgendaViewer)

manage_addAgendaViewerForm = PageTemplateFile(
    "www/agendaViewerAdd", globals(),
    __name__='manage_addAgendaViewerForm')

def manage_addAgendaViewer(self, id, title, REQUEST=None):
    """Add a News AgendaViewer."""
    if not self.is_id_valid(id):
        return
    object = AgendaViewer(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
