import string
# Zope
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
# Silva
from Products.Silva.EditorSupport import EditorSupport
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.IVersionedContent import IVersionedContent
from Products.Silva.helpers import add_and_edit
from Products.ParsedXML.ParsedXML import ParsedXML
from NewsItem import NewsItem, NewsItemVersion
from Interfaces import INewsItem

class Announcement(NewsItem):
    """Silva News Announcement.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News Announcement"

    __implements__ = INewsItem, IVersionedContent

InitializeClass(Announcement)

class AnnouncementVersion(NewsItemVersion):
    """Silva News Announcement version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News Announcement Version"

    def __init__(self, id):
        AnnouncementVersion.inheritedAttribute('__init__')(self, id)
        self.content = ParsedXML('content', '<doc></doc>')

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_announcement_data')
    def set_announcement_data(self, common_info, specific_info, manual_specific_info,
                         target_audiences, subjects, embargo_datetime, more_info_links):
        self._common_info = common_info
        self._specific_info = specific_info
        self._manual_specific_info = manual_specific_info
        self._target_audiences = target_audiences
        self._subjects = subjects
        self._embargo_datetime = embargo_datetime
        self._more_info_links = [item.split('|') for item in more_info_links.split('\n') if item] # Filters out empty lines
        # FIXME: It would be nice if this could be moved upwards in the class-hierarchy
        # reindex is acquired from the object
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_announcement_data_without_subjects_target_audiences')
    def set_announcement_data_without_subjects_target_audiences(self, common_info, specific_info, manual_specific_info,
                         embargo_datetime, more_info_links):
        self._common_info = common_info
        self._specific_info = specific_info
        self._manual_specific_info = manual_specific_info
        self._embargo_datetime = embargo_datetime
        self._more_info_links = [item.split('|') for item in more_info_links.split('\n') if item] # Filters out empty lines
        # FIXME: It would be nice if this could be moved upwards in the class-hierarchy
        # reindex is acquired from the object
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_announcement_data_subjects_target_audiences')
    def set_announcement_data_subjects_target_audiences(self, subjects, target_audiences):
        self._target_audiences = target_audiences
        self._subjects = subjects
        # FIXME: It would be nice if this could be moved upwards in the class-hierarchy
        # reindex is acquired from the object
        self.reindex_object()

    def fulltext(self):
        parenttext = AnnouncementVersion.inheritedAttribute('fulltext')(self)
        content = self._flattenxml(str(self.content))
        return "%s %s" % (parenttext, content)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Returns the content as a partial XML-document
        """
        AnnouncementVersion.inheritedAttribute('to_xml')(self, context)
        xml = u'<content>\n%s\n</content>\n' % self.content_xml()

        context.f.write(xml)

InitializeClass(AnnouncementVersion)

manage_addAnnouncementForm = PageTemplateFile(
    "www/announcementAdd", globals(),
    __name__='manage_addAnnouncementForm')

def manage_addAnnouncement(self, id, title, REQUEST=None):
    """Add a News Announcement."""
    if not self.is_id_valid(id):
        return
    object = Announcement(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object._setObject('0', AnnouncementVersion('0'))
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addAnnouncementVersionForm = PageTemplateFile(
    "www/announcementVersionAdd",
    globals() ,
    __name__='manage_addAnnouncementVersionForm')

def manage_addAnnouncementVersion(self, id, REQUEST=None):
    """Add a Announcement version."""
    object = AnnouncementVersion(id)
    self._setObject(id, object)
    object.reindex_object()
    add_and_edit(self, id, REQUEST)
    return ''
