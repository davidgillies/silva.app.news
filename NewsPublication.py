# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.13 $

from zope.interface import implements
from zope.app.container.interfaces import IObjectAddedEvent

# Zope
from AccessControl import ClassSecurityInfo
try:
    from App.class_init import InitializeClass # Zope 2.12
except ImportError:
    from Globals import InitializeClass # Zope < 2.12

# Silva
from silva.core import conf as silvaconf
from Products.Silva.Publication import Publication
from Products.Silva import SilvaPermissions

# SilvaNews
from Products.SilvaNews.interfaces import INewsItem, INewsPublication

class NewsPublication(Publication):
    """A special publication type (a.k.a. News Source) for news 
    and agenda items. News Filters and Agenda Filters can pick up 
    news from these sources anywhere in a Silva site.
    """
    security = ClassSecurityInfo()

    implements(INewsPublication)
    meta_type = "Silva News Publication"
    silvaconf.icon("www/news_source.png")
    silvaconf.priority(3)

    def __init__(self, id):
        NewsPublication.inheritedAttribute('__init__')(self, id)
        self._addables_allowed_in_container = ['Silva Article', 'Silva Agenda Item', 'Silva Publication', 'Silva Folder']

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'parent_path')
    def parent_path(self):
        """Returns the path of the parent of this source
        """
        return '/'.join(self.aq_inner.aq_parent.getPhysicalPath())
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'idx_parent_path')
    idx_parent_path = parent_path

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_fields_for_bulk_editing')
    def get_fields_for_bulk_editing(self, field_keys, objectids,
                                    startpoint=None):
        """
        Creates a dictionary of values for each field in field_keys,
        if the value is None the field should not be shown (the
        objects do not have the field available at all), if it is a
        string containing '__DO_NOT_FILL_FIELD__', the field should be
        created but not filled (some of the objects have the field,
        but the value is different for them) and if the value is
        something else, the field should be filled (some of the
        objects contain the field, and the value is the same for all
        of them (which is the value of the dictionary-item
        """
        if startpoint is None:
            startpoint = self
        versionpaths = []
        fields = {}
        for key in field_keys:
            fields[key] = None

        # walk through the objects, they should be in direct children of this object
        for item in objectids:
            currentobj = getattr(startpoint, item)
            if INewsItem.providedBy(currentobj):
                version = currentobj.get_editable()
                versionpaths.append(currentobj.getPhysicalPath())
                if not version:
                    # no editable version
                    continue
                for key in fields.keys():
                    if hasattr(version, key):
                        value = getattr(version, key)()
                        if fields[key] is None:
                            fields[key] = value
                        elif fields[key] != value:
                            fields[key] = '__DO_NOT_FILL_FIELD__'
            elif currentobj.implements_container() or currentobj.implements_publication():
                # this is a folder, so walk through it...
                morefields, morepaths = self.get_fields_for_bulk_editing(field_keys, currentobj.objectIds(), currentobj)
                versionpaths += morepaths
                for key in morefields.keys():
                    if fields[key] != morefields[key]:
                        if morefields[key] == '__DO_NOT_FILL_FIELD__':
                            fields[key] = '__DO_NOT_FILL_FIELD__'
                        elif morefields[key] is not None and fields[key] is None:
                            fields[key] = morefields[key]
                        elif morefields[key] is not None and fields[key] is not None:
                            fields[key] = '__DO_NOT_FILL_FIELD__'
        return (fields, versionpaths)

@silvaconf.subscribe(INewsPublication, IObjectAddedEvent)
def np_added(obj, event):
    """news publications should have their 'hide_from_tocs' set to
       'hide'.  This can be done after they are added"""
    binding = obj.service_metadata.getMetadata(obj)
    binding.setValues('silva-extra', {'hide_from_tocs': 'hide'}, reindex=1)
    binding.setValues('snn-np-settings', {'is_private': 'no'}, reindex=1)
    return

InitializeClass(NewsPublication)
