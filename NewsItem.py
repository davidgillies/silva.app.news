# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.17 $

# Python
from StringIO import StringIO

# Zope
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
from Products.ParsedXML.ParsedXML import ParsedXML

# Silva interfaces
from INewsItem import INewsItem, INewsItemVersion

# Silva
from Products.Silva.EditorSupport import EditorSupport
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.IVersionedContent import IVersionedContent
from Products.Silva.helpers import add_and_edit
from Products.Silva.Version import Version

# XXX necessary for override of _update_publication_status
empty_version = (None, None, None)

class NewsItem(CatalogedVersionedContent, EditorSupport):
    """Silva NewsItem, superclass for all kinds of newsitems.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News NewsItem"
    default_catalog = 'service_catalog'

    __implements__ = IVersionedContent

    _is_allowed_in_publication = 0

    def __init__(self, id, title):
        NewsItem.inheritedAttribute("__init__")(self, id, title)
        self._creation_datetime = DateTime()

    # XXX shouldn't this be moved to SilvaObject or so?
    def manage_afterAdd(self, item, container):
        NewsItem.inheritedAttribute('manage_afterAdd')(
            self, item, container)
        container._add_ordered_id(item)
        self.reindex_object()

    def manage_beforeDelete(self, item, container):
        NewsItem.inheritedAttribute('manage_beforeDelete')(
            self, item, container)
        container._remove_ordered_id(item)
        self.unindex_object()

    # MANIPULATORS
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
        if context.last_version == 1:
            version_id = self.get_next_version()
            if version_id is None:
                version_id = self.get_public_version()
        else:
            version_id = self.get_public_version()

        if version_id is None:
            return

        version = getattr(self, version_id)

        version.to_xml(context)

InitializeClass(NewsItem)

class NewsItemVersion(Version, CatalogPathAware):
    """Silva NewsItemVersion superclass.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva NewsItem Version"

    default_catalog = 'service_catalog'

    def __init__(self, id):
        self.id = id
        self._subjects = []
        self._target_audiences = []
        self.content = ParsedXML('content', '<doc></doc>')

    def manage_beforeDelete(self, item, container):
        NewsItemVersion.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.unindex_object()

    # MANIPULATORS -- FOR BULK-EDITING THE SET_DATA-WAY (1 MANIPULATOR FOR ALL THE
    # DATA-FIELDS) DID NOT SUFFICE, THEREFORE THERE WILL BE 1 MANIPULATOR FOR EACH DATA-FIELD.
    # THIS IS AN ADVANTAGE WHEN SUBCLASSING: ONLY A MANIPULATOR PER FIELD-TYPE HAS TO BE WRIITEN
    # (IN THE CLASS THAT HOLDS THE DATA-DEFINITION)
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_subjects')
    def set_subjects(self, subjects):
        self._subjects = subjects
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_target_audiences')
    def set_target_audiences(self, target_audiences):
        self._target_audiences = target_audiences
        self.reindex_object()

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object_title')
    def object_title(self):
        # HACK: happens through acquisition
        return self.get_title_editable()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'subheader')
    def subheader(self):
        """Returns subheader, subheader is the first header in the content (or '' if no headers in content are defined)
        """
        content = self.content
        for child in content.childNodes[0].childNodes:
            if child.nodeName == u'heading':
                return self.render_heading_as_html(child)
        return ''

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'lead')
    def lead(self):
        """Returns lead, lead is the first paragraph of the content (or '' if not paragraph is found)
        """
        content = self.content
        for child in content.childNodes[0].childNodes:
            if child.nodeName == u'p':
                return self.render_text_as_html(child)
        return ''

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'source_path')
    def source_path(self):
        """Returns the path to the source containing this item
        """
        obj = self.aq_inner.aq_parent
        while (obj.getPhysicalPath() != ('',) and
               not obj.meta_type == 'Silva NewsSource'):
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
        if source and self.restrictedTraverse(source).is_private():
            return 1
        else:
            return 0

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
                              'info_item')
    def info_item(self):
        return self._info_item

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Returns all data as a flat string for full text-search
        """
        content = self._flattenxml(self.content_xml())
        return "%s %s %s %s %s" % (self.id,
                                      self.get_title_html(),
                                      " ".join(self._subjects),
                                      " ".join(self._target_audiences),
                                      content)

    def _flattenxml(self, xmlinput):
        """Cuts out all the XML-tags, helper for fulltext (for content-objects)
        """
        # FIXME: should take care of CDATA-chunks as well...
        xmlinput = xmlinput.encode('cp1252')
        while 1:
            ltpos = xmlinput.find('<')
            gtpos = xmlinput.find('>')
            if ltpos > -1 and gtpos > -1:
                xmlinput = xmlinput.replace(xmlinput[ltpos:gtpos + 1], ' ')
            else:
                break
        return xmlinput

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'content_xml')
    def content_xml(self):
        """Returns the documentElement of the content's XML
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
        xml += u'<meta_type>%s</meta_type>\n' % self.meta_type
        xml += u'<content>\n%s\n</content>\n' % self.content_xml()
        for subject in self._subjects:
            xml += u'<subject>%s</subject>\n' % self._prepare_xml(subject)
        for audience in self._target_audiences:
            xml += u'<target_audience>%s</target_audience>\n' % self._prepare_xml(audience)

        context.f.write(xml)

    def _prepare_xml(self, inputstring):
        inputstring = unicode(inputstring, 'cp1252')
        inputstring = inputstring.replace('&', '&amp;')
        inputstring = inputstring.replace('<', '&lt;')
        inputstring = inputstring.replace('>', '&gt;')

        return inputstring

InitializeClass(NewsItemVersion)
