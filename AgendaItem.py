# Zope
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
from Products.ParsedXML.ParsedXML import ParsedXML

# Silva interfaces
from IAgendaItem import IAgendaItem
from INewsItem import INewsItem

# Silva
from Products.Silva.EditorSupport import EditorSupport
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

    __implements__ = INewsItem, IAgendaItem, IVersionedContent

    # ACCESSORS

InitializeClass(AgendaItem)

class AgendaItemVersion(NewsItemVersion):
    """Silva Agenda version.
    """
    security = ClassSecurityInfo()

    def __init__(self, id):
        AgendaItemVersion.inheritedAttribute('__init__')(self, id)
        self.id = id
        self._start_datetime = None
        self._location = ''
        self._location_manual = ''

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_start_datetime')
    def set_start_datetime(self, value):
        self._start_datetime = value
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_location')
    def set_location(self, value):
        self._location = value
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
                              'location')
    def location(self):
        """Returns location
        """
        return self._location

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
        return "%s %s %s" % (parenttext, self._location, self._location_manual)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Returns the content as a partial XML-doc
        """
        AgendaItemVersion.inheritedAttribute('to_xml')(self, context)
        xml = u'<start_datetime>%s</start_datetime>\n' % self._prepare_xml(self._start_datetime.strftime("%d-%m-%Y %H:%M:%S"))
        xml += u'<location>%s</location>\n' % self._prepare_xml(self._location_manual or self._location)

        context.f.write(xml)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_summary_xml')
    def to_summary_xml(self, context):
        """Returns a summary of the content as a partial XML-doc (for NewsBundle)
        """
        AgendaItemVersion.inheritedAttribute('to_summary_xml')(self, context)
        xml = u'<start_datetime>%s</start_datetime>\n' % self._prepare_xml(self._start_datetime.strftime("%d-%m-%Y %H:%M:%S"))
        xml += u'<location>%s</location>\n' % self._prepare_xml(self._location_manual or self._location)

        context.f.write(xml)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_small_xml')
    def to_small_xml(self, context):
        """Returns a small version of the content as a partial XML-doc (for NewsBundle)
        """
        AgendaItemVersion.inheritedAttribute('to_summary_xml')(self, context)
        xml = u'<start_datetime>%s</start_datetime>\n' % self._prepare_xml(self._start_datetime.strftime("%d-%m-%Y %H:%M:%S"))
        xml += u'<location>%s</location>\n' % self._prepare_xml(self._location_manual or self._location)

        context.f.write(xml)

InitializeClass(AgendaItemVersion)
