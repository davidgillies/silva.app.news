# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.12 $

# Zope
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
from Products.ParsedXML.ParsedXML import ParsedXML

# Silva interfaces
from IAgendaItem import IAgendaItem, IAgendaItemVersion
from INewsItem import INewsItem, INewsItemVersion

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.IVersionedContent import IVersionedContent
from Products.Silva.helpers import add_and_edit

# SilvaNews
from NewsItem import NewsItem, NewsItemVersion

class AgendaItem(NewsItem):
    """Silva AgendaItem, superclass for some agendaitems
    """
    security = ClassSecurityInfo()

    __implements__ = IAgendaItem, IVersionedContent

    # ACCESSORS

InitializeClass(AgendaItem)

class AgendaItemVersion(NewsItemVersion):
    """Silva Agenda version.
    """
    security = ClassSecurityInfo()

    __implements__ = IAgendaItemVersion

    def __init__(self, id):
        AgendaItemVersion.inheritedAttribute('__init__')(self, id)
        self.id = id
        self._start_datetime = None
        self._location_manual = ''

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_start_datetime')
    def set_start_datetime(self, value):
        self._start_datetime = value
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_location_manual')
    def set_location_manual(self, value):
        self._location_manual = value
        self.reindex_object()

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'start_datetime')
    def start_datetime(self):
        """Returns the start date/time
        """
        return self._start_datetime

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'location_manual')
    def location_manual(self):
        """Returns location manual
        """
        return self._location_manual

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Deliver the contents as plain text, for full-text search
        """
        parenttext = AgendaItemVersion.inheritedAttribute('fulltext')(self)
        return "%s %s" % (parenttext, self._location_manual)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Returns the content as a partial XML-doc
        """
        AgendaItemVersion.inheritedAttribute('to_xml')(self, context)
        xml = u'<start_datetime>%s</start_datetime>\n' % self._prepare_xml(self._start_datetime.rfc822())
        xml += u'<location>%s</location>\n' % self._prepare_xml(self._location_manual)

        context.f.write(xml)

InitializeClass(AgendaItemVersion)
