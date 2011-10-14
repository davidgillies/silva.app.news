# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.i18nmessageid import MessageFactory

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.cataloging import CatalogingAttributesVersion

from silva.app.document import document
from silva.core import conf as silvaconf
from silva.core.interfaces import IRoot
from silva.core.interfaces.events import IContentPublishedEvent
from silva.core.services.interfaces import ICataloging

from silva.app.news.interfaces import INewsItem, INewsItemVersion
from silva.app.news.interfaces import INewsPublication, INewsViewer
from silva.app.news.datetimeutils import (datetime_to_unixtimestamp,
    CalendarDatetime)
from silva.app.news.NewsCategorization import NewsCategorization

_ = MessageFactory('silva_news')


class NewsItemVersion(NewsCategorization, document.DocumentVersion):
    """Base class for news item versions.
    """
    security = ClassSecurityInfo()
    grok.implements(INewsItemVersion)
    meta_type = "Silva Article Version"

    def __init__(self, id):
        super(NewsItemVersion, self).__init__(id)
        self._display_datetime = None

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
        SilvaPermissions.AccessContentsInformation, 'get_display_datetime')
    def get_display_datetime(self):
        """returns the display datetime

            see 'set_display_datetime'
        """
        return self._display_datetime

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
        """Returns all data as a flat string for full text-search
        """
        keywords = list(self._subjects)
        keywords.extend(self._target_audiences)
        keywords.extend(super(NewsItemVersion, self).fulltext())
        return keywords


InitializeClass(NewsItemVersion)


class NewsItem(document.Document):
    """A News item that appears as an individual page. By adjusting
       settings the Author can determine which subjects, and
       for which audiences the Article should be presented.
    """
    grok.implements(INewsItem)
    security = ClassSecurityInfo()
    meta_type = "Silva Article"
    silvaconf.icon("www/news_item.png")
    silvaconf.priority(3.7)
    silvaconf.version_class(NewsItemVersion)

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

InitializeClass(NewsItem)


class NewsItemVersionCatalogingAttributes(CatalogingAttributesVersion):
    grok.context(INewsItemVersion)

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


@grok.subscribe(INewsItemVersion, IContentPublishedEvent)
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


