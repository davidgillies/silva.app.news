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
from AgendaItem import AgendaItem, AgendaItemVersion
from Interfaces import INewsItem, IAgendaItem

class Event(AgendaItem):
    """Silva News Event.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News Event"

    __implements__ = INewsItem, IAgendaItem, IVersionedContent

InitializeClass(Event)

class EventVersion(AgendaItemVersion):
    """Silva News Event version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News Event Version"

    def __init__(self, id):
        EventVersion.inheritedAttribute('__init__')(self, id)
        self._speakers = ''
        self._end_datetime = None
        self.content = ParsedXML('content', '<doc></doc>')

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_event_data')
    def set_event_data(self, speakers, start_datetime, end_datetime,
                       location, location_manual, common_info, specific_info, manual_specific_info,
                       target_audiences, subjects, embargo_datetime, more_info_links):
        self._speakers = speakers
        self._start_datetime = start_datetime
        self._end_datetime = end_datetime
        self._location = location
        self._location_manual = location_manual
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
                              'set_event_data_without_subjects_target_audiences')
    def set_event_data_without_subjects_target_audiences(self, speakers, start_datetime, end_datetime,
                       location, location_manual, common_info, specific_info, manual_specific_info,
                       embargo_datetime, more_info_links):
        self._speakers = speakers
        self._start_datetime = start_datetime
        self._end_datetime = end_datetime
        self._location = location
        self._location_manual = location_manual
        self._common_info = common_info
        self._specific_info = specific_info
        self._manual_specific_info = manual_specific_info
        self._embargo_datetime = embargo_datetime
        self._more_info_links = [item.split('|') for item in more_info_links.split('\n') if item] # Filters out empty lines
        # FIXME: It would be nice if this could be moved upwards in the class-hierarchy
        # reindex is acquired from the object
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_event_data_subjects_target_audiences')
    def set_event_data_subjects_target_audiences(self, subjects, target_audiences):
        self._subjects = subjects
        self._target_audiences = target_audiences
        # FIXME: It would be nice if this could be moved upwards in the class-hierarchy
        # reindex is acquired from the object
        self.reindex_object()

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'end_datetime')
    def end_datetime(self):
        """Returns the end-date/time
        """
        return self._end_datetime

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'speakers')
    def speakers(self):
        """Returns the speakers
        """
        return self._speakers

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Deliver the contents as plain text, for full-text search
        """
        parenttext = EventVersion.inheritedAttribute('fulltext')(self)
        content = self._flattenxml(str(self.content))
        return "%s %s %s %s" % (parenttext, self._speakers, self._end_datetime, content)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Returns the content as a partial XML-document
        """
        EventVersion.inheritedAttribute('to_xml')(self, context)
        xml = u'<speakers>%s</speakers>\n' % self._prepare_xml(self._speakers)
        xml += u'<end_datetime>\n%s\n</end_datetime>\n' % self._end_datetime
        xml += u'<content>\n%s\n</content>\n' % self.content_xml()

        context.f.write(xml)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_summary_xml')
    def to_summary_xml(self, context):
        """Returns a summary of the content as a partial XML-doc (for NewsBundle)
        """
        EventVersion.inheritedAttribute('to_summary_xml')(self, context)
        xml = u'<speakers>%s</speakers>\n' % self._prepare_xml(self._speakers)

        context.f.write(xml)


InitializeClass(EventVersion)

manage_addEventForm = PageTemplateFile(
    "www/eventAdd", globals(),
    __name__='manage_addEventForm')

def manage_addEvent(self, id, title, REQUEST=None):
    """Add a News Event."""
    if not self.is_id_valid(id):
        return
    object = Event(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object._setObject('0', EventVersion('0'))
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addEventVersionForm = PageTemplateFile(
    "www/eventVersionAdd",
    globals() ,
    __name__='manage_addEventVersionForm')

def manage_addEventVersion(self, id, REQUEST=None):
    """Add a Event version."""
    object = EventVersion(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''
