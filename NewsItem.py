# Python
from StringIO import StringIO
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
from Products.Silva.VersionedContent import CataloguedVersionedContent
from Products.Silva.IVersionedContent import IVersionedContent
from Products.Silva.helpers import add_and_edit
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva.Version import Version
from Interfaces import INewsItem

# XXX necessary for override of _update_publication_status
empty_version = (None, None, None)

class NewsItem(CataloguedVersionedContent, EditorSupport):
    """Silva News NewsItem, superclass for all kinds of newsitems.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News NewsItem"
    default_catalog = 'service_catalog'

    __implements__ = IVersionedContent, INewsItem

    def __init__(self, id, title):
        NewsItem.inheritedAttribute("__init__")(self, id, title)
        self._creation_datetime = DateTime()

    # MANIPULATORS
    # XXX shouldn't this be moved to SilvaObject or so?
    def manage_afterAdd(self, item, container):
        container._add_ordered_id(item)

    def manage_beforeDelete(self, item, container):
        NewsItem.inheritedAttribute('manage_beforeDelete')(self, item, container)
        container._remove_ordered_id(item)

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'creation_datetime')
    def creation_datetime(self):
        return self._creation_datetime

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Maps to the most useful(?) version (public, else unapproved or approved)
        """
        version = self.get_viewable() or self.get_previewable()
        version.to_xml(context)

InitializeClass(NewsItem)

class NewsItemVersion(Version, CatalogPathAware):
    """Silva EUR NewsItemVersion superclass.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva EUR NewsItem Version"

    #__implements__ = Interfaces.Version

    default_catalog = 'service_catalog'

    def __init__(self, id):
        NewsItemVersion.inheritedAttribute('__init__')(self, id)
        self.id = id
        self._common_info = ''
        self._specific_info = ''
        self._manual_specific_info = ''
        self._subjects = []
        self._target_audiences = []
        self._embargo_datetime = None
        self._more_info_links = []

    # MANIPULATORS
    # To be added in subclasses

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object_title')
    def object_title(self):
        # HACK: happens through acquisition
        return self.get_title()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'source_path')
    def source_path(self):
        """Returns the path to the source containing this item
        """
        obj = self.aq_inner.aq_parent
        while obj.getPhysicalPath() != ('',) and not obj.meta_type == 'Silva News NewsSource':
            obj = obj.aq_parent
        if obj.getPhysicalPath() != ('',):
            return '/'.join(obj.getPhysicalPath())
        else:
            return None

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_private')
    def is_private(self):
        """Returns whether the object is in a private source
        """
        source = self.source_path()
        if source and source.restrictedTraverse().is_private():
            return 1
        else:
            return 0

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'embargo_datetime')
    def embargo_datetime(self):
        """Returns the embargo datetime
        """
        return self._embargo_datetime

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'common_info')
    def common_info(self):
        """Returns common info
        """
        return self._common_info

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'specific_info')
    def specific_info(self):
        """Returns specific info
        """
        return self._specific_info

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'manual_specific_info')
    def manual_specific_info(self):
        """Returns manual specific info
        """
        return self._manual_specific_info

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'subjects')
    def subjects(self):
        """Returns the subjects
        """
        return self._subjects

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'target_audiences')
    def target_audiences(self):
        """Returns the target audiences
        """
        return self._target_audiences

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'more_info_links')
    def more_info_links(self):
        """Returns the links
        """
        return self._more_info_links

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Returns all data as a flat string for full text-search
        """
        return "%s %s %s %s %s %s" % (self.id,
                                      self.get_title(),
                                      self._common_info,
                                      self._manual_specific_info or self._specific_info,
                                      " ".join(self._subjects),
                                      " ".join(self._target_audiences))

    def _flattenxml(self, xmlinput):
        """Cuts out all the XML-tags, helper for fulltext (for content-objects)
        """
        # FIXME: should take care of CDATA-chunks as well...
        while 1:
            ltpos = xmlinput.find('<')
            gtpos = xmlinput.find('>')
            if ltpos > -1 and gtpos > -1:
                xmlinput = xmlinput.replace(xmlinput[ltpos:gtpos + 1], '')
            else:
                break
        return xmlinput

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'content_documentElement_xml')
    def content_xml(self):
        """Returns the documentElement of the content's XML
        WILL BE USED IN SOME BUT NOT ALL SUBCLASSES but would be messy to move it to those classes
        """
        s = StringIO()
        self.content.documentElement.writeStream(s)
        value = s.getvalue()
        s.close()
        return value

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Returns the content as a partial XML-document
        """
        xml = u'<title>%s</title>\n' % self.get_title()
        xml += u'<common_info>%s</common_info>\n' % self._prepare_xml(self._common_info)
        xml += u'<specific_info>%s</specific_info>\n' % self._prepare_xml(self._manual_specific_info or self._specific_info)
        xml += u'<embargo_datetime>%s</embargo_datetime>\n' % self._prepare_xml(self._embargo_datetime)
        for subject in self._subjects:
            xml += u'<subject>%s</subject>\n' % self._prepare_xml(subject)
        for audience in self._target_audiences:
            xml += u'<target_audience>%s</target_audience>\n' % self._prepare_xml(audience)
        for pair in self._more_info_links:
            xml += u'<link>\n'
            if pair.find('|') > -1:
                url, text = pair.split('|')
                xml += u'<url>%s</url>\n' % self._prepare_xml(url)
                xml += u'<text>%s</url>\n' % self._prepare_xml(text)
            else:
                xml += u'<url>%s</url>\n' % self._prepare_xml(pair)
            xml += u'</link>\n'

        context.f.write(xml)


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_summary_xml')
    def to_summary_xml(self, context):
        """Returns a summary of the content as a partial XML-doc (for NewsBundle)
        """
        xml = u'<title>%s</title>\n' % self.get_title()
        xml += u'<common_info>%s</common_info>\n' % self._prepare_xml(self._common_info)
        xml += u'<specific_info>%s</specific_info>\n' % self._prepare_xml(self._manual_specific_info or self._specific_info)

        context.f.write(xml)
    def _prepare_xml(self, inputstring):
        inputstring = unicode(inputstring, 'cp1252')
        inputstring = inputstring.replace('&', '&amp;')
        inputstring = inputstring.replace('<', '&lt;')
        inputstring = inputstring.replace('>', '&gt;')

        return inputstring

InitializeClass(NewsItemVersion)
