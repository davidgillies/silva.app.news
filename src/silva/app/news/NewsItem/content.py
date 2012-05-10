# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.i18nmessageid import MessageFactory

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime

from Products.Silva import SilvaPermissions
from Products.Silva.cataloging import CatalogingAttributesVersion

from silva.app.document.document import DocumentContent
from silva.app.document.document import DocumentContentVersion
from silva.core import conf as silvaconf
from silva.core.interfaces import IRoot
from silva.core.interfaces.events import IContentPublishedEvent
from silva.core.services.interfaces import ICataloging

from ..NewsCategorization import NewsCategorization
from ..datetimeutils import datetime_to_unixtimestamp, CalendarDatetime
from ..interfaces import INewsItem, INewsItemVersion
from ..interfaces import INewsItemContent, INewsItemContentVersion
from ..interfaces import INewsPublication, INewsViewer

_ = MessageFactory('silva_news')


# We cannot inherit from Version here, its __init__ is buggy (use Zope 2)
class NewsItemContentVersion(NewsCategorization):
    grok.baseclass()
    grok.implements(INewsItemContentVersion)
    security = ClassSecurityInfo()

    _external_url = None
    _display_datetime = None

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_display_datetime')
    def set_display_datetime(self, ddt):
        """set the display datetime

            this datetime is used to determine whether an item should be shown
            in the news viewer, and to determine the order in which the items
            are shown
        """
        self._display_datetime = DateTime(ddt)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_external_url')
    def set_external_url(self, url):
        self._external_url = url

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_display_datetime')
    def get_display_datetime(self):
        """returns the display datetime

            see 'set_display_datetime'
        """
        return self._display_datetime

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_external_url')
    def get_external_url(self):
        return self._external_url

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
        """Returns all data as a flat string for full text-search
        """
        keywords = list(self._subjects)
        keywords.extend(self._target_audiences)
        keywords.extend(super(NewsItemContentVersion, self).fulltext())
        return keywords


InitializeClass(NewsItemContentVersion)


class NewsItemVersion(NewsItemContentVersion, DocumentContentVersion):
    """Base class for news item versions.
    """
    grok.implements(INewsItemVersion)
    meta_type = "Silva News Item Version"
    security = ClassSecurityInfo()


InitializeClass(NewsItemVersion)

# We cannot inherit from VersionedContent here (__init__ buggy)
class NewsItemContent(object):
    grok.baseclass()
    grok.implements(INewsItemContent)
    security = ClassSecurityInfo()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_unapproved_version_display_datetime')
    def set_unapproved_version_display_datetime(self, dt):
        """Set display datetime for unapproved
        """
        version = getattr(self, self.get_unapproved_version())
        version.set_display_datetime(dt)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_unapproved_version_display_datetime')
    def get_unapproved_version_display_datetime(self):
        """get display datetime for unapproved
        """
        version = getattr(self, self.get_unapproved_version())
        version.get_display_datetime()


InitializeClass(NewsItemContent)


class NewsItem(NewsItemContent, DocumentContent):
    """A News item that appears as an individual page. By adjusting
       settings the Author can determine which subjects, and
       for which audiences the Article should be presented.
    """
    grok.implements(INewsItem)
    security = ClassSecurityInfo()
    meta_type = "Silva News Item"
    silvaconf.icon("www/news_item.png")
    silvaconf.priority(-7)
    silvaconf.version_class(NewsItemVersion)


InitializeClass(NewsItem)


class NewsItemContentVersionCatalogingAttributes(CatalogingAttributesVersion):
    grok.context(INewsItemContentVersion)

    def sort_index(self):
        dt = self.context.get_display_datetime()
        if dt:
            return datetime_to_unixtimestamp(dt)
        return None

    def timestamp_ranges(self):
        dt = self.context.get_display_datetime()
        if dt is not None:
            return CalendarDatetime(dt, None).get_unixtimestamp_ranges()
        return None

    def display_datetime(self):
        return self.context.get_display_datetime()

    def subjects(self):
        return self.context.get_subjects()

    def target_audiences(self):
        return self.context.get_target_audiences()


@grok.subscribe(INewsItemContentVersion, IContentPublishedEvent)
def news_item_published(version, event):
    if version.get_display_datetime() is None:
        version.set_display_datetime(DateTime())
        ICataloging(version).reindex()


@grok.adapter(INewsItem)
@grok.implementer(INewsViewer)
def get_default_viewer(context):
    """Adapter factory to get the contextual news viewer for a news item
    """
    parents = context.aq_chain[1:]
    for parent in parents:
        if IRoot.providedBy(parent):
            return None
        if INewsViewer.providedBy(parent):
            return parent
        if INewsPublication.providedBy(parent):
            default = parent.get_default()
            if default and INewsViewer.providedBy(default):
                return default
    return None


