# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
# Silva
from Products.Silva.Publication import Publication
from Products.Silva.IPublication import IPublication
from Products.Silva import SilvaPermissions
#misc
from Products.Silva.helpers import add_and_edit

class NewsSource(Publication, CatalogPathAware):
    """Source
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News NewsSource"

    __implements__ = IPublication

    default_catalog = 'service_catalog'

    def __init__(self, id, title):
        NewsSource.inheritedAttribute('__init__')(self, id, title)
        self._is_private = 0

    def manage_afterAdd(self, item, container):
        NewsSource.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.index_object()

    def manage_beforeDelete(self, item, container):
        NewsSource.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.unindex_object()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object_title')
    def object_title(self):
        return self._title

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_private')
    def is_private(self):
        """Returns the private-state
        """
        return self._is_private

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'source_path')
    def parent_path(self):
        """Returns the path of this source
        """
        return '/'.join(self.aq_inner.aq_parent.getPhysicalPath())

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_private')
    def set_private(self, on_or_off):
        """Sets the is_private-setting for this source, is_private can restrict the
        availability of this source towards the outside-world (when set, the source
        can only be found by filters in the same subdirectory)
        """
        self._is_private = on_or_off
        self.reindex_object()
        self._p_changed = 1
        self.reindex_object()

InitializeClass(NewsSource)

manage_addNewsSourceForm = PageTemplateFile("www/newsSourceAdd", globals(),
                                             __name__='manage_addNewsSourceForm')

def manage_addNewsSource(self, id, title, create_default=1, REQUEST=None):
    """Add a Silva Newssource."""
    if not self.is_id_valid(id):
        return
    object = NewsSource(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
