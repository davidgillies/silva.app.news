# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
import OFS
# Silva
from Products.Silva.Asset import Asset
from Products.Silva.IAsset import IAsset
import Products.Silva.SilvaPermissions as SilvaPermissions
# misc
from Products.Silva.helpers import add_and_edit

from Interfaces import INewsItem

class MetaTypeException(Exception):
    pass

class Filter(Asset, CatalogPathAware):
    """Filter object, a small object that shows a couple
    of different screens to different users, a filter for all NewsItem-objects
    to the editor and a filter (containing some different info) for all
    published NewsItem-objects for the end-users.
    """
    security = ClassSecurityInfo()
    __implements__ = IAsset
    default_catalog = 'service_catalog'

    _sources = []

    def __init__(self, id, title):
        Filter.inheritedAttribute('__init__')(self, id, title)
        #self._allowed_meta_types = ['Silva News Article', 'Silva News Announcement', 'Silva News Event', 'Silva News Oration', 'Silva News Promotion', 'Silva News ValedictoryLecture']
        self._keep_to_path = 1
        self._subjects = {}
        self._target_audiences = {}
        self._catalog = 'service_catalog'
        self._excluded_items = []

    def manage_afterAdd(self, item, container):
        Filter.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.index_object()

    def manage_beforeDelete(self, item, container):
        Filter.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.unindex_object()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'find_sources')
    def find_sources(self):
        """Returns all the sources available for querying
        """
        query = {'meta_type': ['Silva News NewsSource'], 'sort_on': 'id', 'is_private': 0}
        results = self.service_catalog(query)
        query['is_private'] = 1
        query['parent_path'] = '/'.join(self.aq_inner.aq_parent.getPhysicalPath())
        results += self.service_catalog(query)
        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sources')
    def sources(self):
        """Returns the list of sources
        """
        self.verify_sources()
        if not self._sources:
            self._sources = []
        return self._sources

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'add_source')
    def add_source(self, sourcepath, add_or_remove):
        """Add a source
        """
        if not self._sources:
            self._sources = []
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
        print "Allowed sources: %s" % allowedsources
        print "Currentsources: %s" % self._sources
        for source in self._sources:
            if not source in allowedsources:
                self._sources.remove(source)
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'excluded_items')
    def excluded_items(self):
        """Returns a list of object-paths of all excluded items
        """
        return self._excluded_items

    def verify_excluded_items(self):
        for item in self._excluded_items:
            query = {'object_path': item}
            result = self.aq_inner.service_catalog(query)
            if not result:
                self._excluded_items.remove(item)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'keep_to_path')
    def keep_to_path(self):
        """Returns true if the item should keep to path
        THIS METHOD IS NOT IN USE RIGHT NOW... delete?
        """
        return self._keep_to_path

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'subjects')
    def subjects(self):
        """Returns a list of subjects
        """
        return self._subjects.keys()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'target_audiences')
    def target_audiences(self):
        """Returns a list of target audiences
        """
        return self._target_audiences.keys()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_keep_to_path')
    def set_keep_to_path(self, value):
        """Sets the keep_to_path property to restrict the searcharea of the browser
        THIS METHOD IS NOT IN USE RIGHT NOW... delete?
        """
        # make sure the var will contain either 0 or 1
        self._keep_to_path = not not value
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_subject')
    def set_subject(self, subject, on_or_off):
        """Updates the list of subjects
        """
        if on_or_off:
            self._subjects[subject] = 1
        else:
            if self._subjects.has_key(subject):
                del self._subjects[subject]
        self._p_changed = 1
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_target_audience')
    def set_target_audience(self, target_audience, on_or_off):
        """Updates the list of target_audiences
        """
        if on_or_off:
            self._target_audiences[target_audience] = 1
        else:
            if self._target_audiences.has_key(target_audience):
                del self._target_audiences[target_audience]
        self._p_changed = 1
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'synchronize_with_service')
    def synchronize_with_service(self):
        """Checks whether the lists of subjects and target_audiences
        only contain items that the service_news-lists contain (to remove
        items from the object's list that are removed in the service)
        """
        service_subjects = self.service_news.subjects()
        service_target_audiences = self.service_news.target_audiences()

        removed_subjects = []
        removed_target_audiences = []

        for key in self._subjects.keys():
            if key not in service_subjects:
                removed_subjects.append(key)
                del self._subjects[key]

        for key in self._target_audiences.keys():
            if key not in service_target_audiences:
                removed_target_audiences.append(key)
                del self._target_audiences[key]

        self.reindex_object()
        return removed_subjects + removed_target_audiences

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

InitializeClass(Filter)
