# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.30 $

# Python
from StringIO import StringIO

# Zope
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
from Products.ParsedXML.ParsedXML import ParsedXML

# Silva interfaces
from Products.SilvaNews.interfaces import INewsItem, INewsItemVersion

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.interfaces import IVersionedContent
from Products.Silva.helpers import add_and_edit
from Products.SilvaDocument.Document import DocumentVersion
from Products.Silva.Metadata import export_metadata

from Products.SilvaDocument import mixedcontentsupport

class NewsItem(CatalogedVersionedContent):
    """Base class for all kinds of news items.
    """
    security = ClassSecurityInfo()

    __implements__ = IVersionedContent

    # MANIPULATORS

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Maps to the most useful(?) version
        (public, else unapproved or approved)
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

        context.f.write('<silva_newsitem id="%s">' % self.id)
        version.to_xml(context)
        context.f.write('</silva_newsitem>')

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'implements_newsitem')
    def implements_newsitem(self):
        return True

InitializeClass(NewsItem)

class NewsItemVersion(DocumentVersion):
    """Base class for news item versions.
    XXX making this subclass DocumentVersion does restrict matters,
    but is clearer than doing the same thing in here again which was
    the case before.
    """
    security = ClassSecurityInfo()

    def __init__(self, id):
        # XXX dummy title?
        NewsItemVersion.inheritedAttribute('__init__')(self, id, 'dummy')
        self._subjects = []
        self._target_audiences = []
        self._display_datetime = None

    # XXX I would rather have this get called automatically on setting 
    # the publication datetime, but that would have meant some nasty monkey-
    # patching would be required...
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'set_display_datetime')
    def set_display_datetime(self, ddt):
        """set the display datetime

            this datetime is used to determine whether an item should be shown
            in the news viewer, and to determine the order in which the items 
            are shown
        """
        self._display_datetime = ddt
        self.reindex_object()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'display_datetime')
    def display_datetime(self):
        """returns the display datetime

            see 'set_display_datetime'
        """
        return self._display_datetime

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'idx_display_datetime')
    idx_display_datetime = display_datetime
        
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
                              'get_intro')
    def get_intro(self, max_size=1024):
        """Returns first bit of the news item's content

            this returns all elements up to and including the first
            paragraph, if it turns out that there are more than max_size
            characters in the data returned it will truncate (per element)
            to minimally 1 element
        """
        content = self.content
        ret = []
        length = 0
        for child in content.childNodes[0].childNodes:
            if child.nodeName == 'image':
                continue
            # XXX the viewer is set every iteration because the renderView
            # calls of certain elements will set it to something else
            self.service_editor.setViewer('service_news_sub_viewer')
            add = self.service_editor.renderView(child)
            if type(add) != unicode:
                add = unicode(add, 'UTF-8')
            if len(add) + length > max_size:
                if ret:
                    return '\n'.join(ret)
                return add
            length += len(add)
            ret.append(add)
            # break after the first <p> node
            #if child.nodeName == 'p':
            #    break
        return '\n'.join(ret)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_thumbnail')
    def get_thumbnail(self, divclass=None):
        """returns an image tag for the tumbnail of the first image in the item

            returns '' if no image is available
        """
        images = self.content.documentElement.getElementsByTagName('image')
        if not images:
            return ''
        imgpath = images[0].getAttribute('path').split('/')
        img = self.restrictedTraverse(imgpath)
        if not img:
            return '[broken image]'
        tag = ('<a class="newsitem_thumbnail_link" href="%s">%s</a>' % 
                    (self.object().absolute_url(), img.tag(thumbnail=1)))
        if divclass:
            tag = '<div class="%s">%s</div>' % (divclass, tag)
        return tag
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_description')
    def get_description(self):
        binding = self.service_metadata.getMetadata(self)
        desc = binding.get('silva-extra', 'content_description')
        return desc
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'source_path')
    def source_path(self):
        """Returns the path to the source containing this item
        """
        obj = self.aq_inner.aq_parent
        while (obj.getPhysicalPath() != ('',) and
               not obj.meta_type == 'Silva News Publication'):
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
        # XXX why not rely on acquisition from source?
        source = self.source_path()
        if source and self.restrictedTraverse(source).is_private():
            return 1
        else:
            return 0

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'idx_is_private')
    idx_is_private = is_private

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'subjects')
    def subjects(self):
        """Returns the subjects
        """
        return self._subjects

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'idx_subjects')
    idx_subjects = subjects

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'target_audiences')
    def target_audiences(self):
        """Returns the target audiences
        """
        return self._target_audiences

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'idx_target_audiences')
    idx_target_audiences = target_audiences

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'info_item')
    def info_item(self):
        return self._info_item

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'last_author_fullname')
    def last_author_fullname(self):
        """Returns the userid of the last author, to be used in
        combination with the ZCatalog.  The data this method returns
        can, in opposite to the sec_get_last_author_info data, be
        stored in the ZCatalog without any problems.
        """
        return self.sec_get_last_author_info().fullname()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Returns all data as a flat string for full text-search
        """
        s = StringIO()
        self.content.documentElement.writeStream(s)
        content = self._flattenxml(s.getvalue())
        return "%s %s %s %s" % (self.get_title(),
                                      " ".join(self._subjects),
                                      " ".join(self._target_audiences),
                                      content)
 
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Returns the content as a partial XML-document
        """
        export_metadata(self, context)

        f = context.f
        f.write(u'<title>%s</title>' % self.get_title())
        f.write(u'<meta_type>%s</meta_type>' % self.meta_type)
        f.write(u'<content>')
        self.content_xml(context)
        f.write(u'</content>')
        self.content.documentElement.writeStream(f)

    def content_xml(self, context):
        """Writes all content elements to the XML stream"""
        f = context.f
        for subject in self._subjects:
            f.write(u'<subject>%s</subject>' % self._prepare_xml(subject))
        for audience in self._target_audiences:
            f.write(u'<target_audience>%s</target_audience>' % self._prepare_xml(audience))
    
    def _prepare_xml(self, inputstring):
        inputstring = inputstring.replace(u'&', u'&amp;')
        inputstring = inputstring.replace(u'<', u'&lt;')
        inputstring = inputstring.replace(u'>', u'&gt;')

        return inputstring

InitializeClass(NewsItemVersion)
