# Zope
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
from Products.ParsedXML.ParsedXML import ParsedXML

# Silva interfaces
from Products.Silva.IVersionedContent import IVersionedContent
from Products.SilvaNews.INewsItem import INewsItem
from Products.SilvaNews.IAgendaItem import IAgendaItem, IAgendaItemVersion

# Silva
from Products.Silva.EditorSupport import EditorSupport
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.helpers import add_and_edit
from AgendaItem import AgendaItem, AgendaItemVersion

class PlainAgendaItem (AgendaItem):
    """Silva News AgendaItem
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News PlainAgendaItem"

    __implements__ = IAgendaItem, IVersionedContent

InitializeClass(PlainAgendaItem)

class PlainAgendaItemVersion(AgendaItemVersion):
    """Silva News PlainAgendaItemVersion
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News PlainAgendaItem Version"

    __implements__ = IAgendaItemVersion

    def __init__(self, id):
        PlainAgendaItemVersion.inheritedAttribute('__init__')(self, id)
        self.content = ParsedXML('content', '<doc></doc>')

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Deliver the contents as plain text, for full-text search
        """
        parenttext = PlainAgendaItemVersion.inheritedAttribute('fulltext')(self)
        content = self._flattenxml(repr(self.content))
        return "%s %s" % (parenttext, content)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Returns the content as a partial XML-document
        """
        PlainAgendaItemVersion.inheritedAttribute('to_xml')(self, context)
        xml = u'<content>\n%s\n</content>\n' % self.content_xml()

        context.f.write(xml)

InitializeClass(PlainAgendaItemVersion)

manage_addPlainAgendaItemForm = PageTemplateFile(
    "www/plainAgendaItemAdd", globals(),
    __name__='manage_addPlainAgendaItemForm')

def manage_addPlainAgendaItem(self, id, title, REQUEST=None):
    """Add a News PlainAgendaItem."""
    if not self.is_id_valid(id):
        return
    object = PlainAgendaItem(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object._setObject('0', PlainAgendaItemVersion('0'))
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addPlainAgendaItemVersionForm = PageTemplateFile(
    "www/plainAgendaItemVersionAdd",
    globals() ,
    __name__='manage_addPlainAgendaItemVersionForm')

def manage_addPlainAgendaItemVersion(self, id, REQUEST=None):
    """Add a PlainAgendaItem version."""
    object = PlainAgendaItemVersion(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''
