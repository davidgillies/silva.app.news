# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: newsprovider.py,v 1.3 2005/05/02 14:22:52 guido Exp $
#
from AccessControl import ModuleSecurityInfo
from AccessControl import ClassSecurityInfo
from Acquisition import Explicit
from App.class_init import InitializeClass
from DateTime import DateTime

from five import grok
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.component import getUtility
from zope.interface import Interface
from zope.traversing.browser import absoluteURL
from zope.cachedescriptors.property import Lazy

from Products.Silva import SilvaPermissions
from Products.SilvaMetadata.interfaces import IMetadataService
from silva.app.document.interfaces import IDocumentDetails
from silva.app.news.interfaces import IAgendaItemContentVersion
from silva.app.news.interfaces import INewsItemContentVersion
from silva.app.news.interfaces import INewsItemReference
from silva.app.news.interfaces import INewsViewer, IRSSAggregator


module_security = ModuleSecurityInfo(
    'silva.app.news.codesources.inline')


class INewsProvider(Interface):
    """is able to provide news items"""

    def get_items(self, number, request):
        """returns a set of the most current items"""


class NewsViewerNewsProvider(grok.Adapter):
    """Works for BOTH News and Agenda Viewers!"""
    grok.context(INewsViewer)
    grok.implements(INewsProvider)

    def get_items(self, request, number):
        results = self.context.get_items()
        for item in results[:number]:
            info = getMultiAdapter(
                (item.getObject(), request),
                INewsItemReference)
            info.__parent__ = self.context
            yield info


class NewsItemReference(grok.MultiAdapter):
    """a temporary object to wrap a newsitem"""
    grok.adapts(INewsItemContentVersion, Interface)
    grok.implements(INewsItemReference)
    grok.provides(INewsItemReference)

    security = ClassSecurityInfo()

    def __init__(self, context, request):
        self.context = context
        self.content = context.get_content()
        self.request = request
        self.details = queryMultiAdapter(
            (self.context, self.request), IDocumentDetails)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'id')
    def id(self):
        return self.content.id

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'title')
    def title(self):
        return self.context.get_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'description')
    def description(self, maxchars=1024):
        # we can be sure there is no markup here, so just limit
        desc = getUtility(IMetadataService).getMetadataValue(
            self.context, 'silva-extra', 'content_description')
        if desc is None:
            return ''
        if maxchars > 0:
          desc = desc[:maxchars]
        return desc

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'link')
    def link(self):
        return absoluteURL(self.content, self.request)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'thumbnail')
    def thumbnail(self):
        if self.details is not None:
            thumbnail = self.details.get_thumbnail()
            if thumbnail:
                return """<div class="inv_thumbnail">
  <a class="newsitemthumbnaillink" href="%s">
    %s
  </a>
</div>""" % (self.link(), thumbnail)
        return ''

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'introduction')
    def introduction(self, maxchars=1024):
        if self.details is not None:
            return self.details.get_introduction(length=maxchars)
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'creation_datetime')
    def creation_datetime(self):
        datetime = self.context.get_display_datetime()
        if datetime is not None:
            return datetime
        return getUtility(IMetadataService).getMetadataValue(
            self.context, 'silva-extra', 'publicationtime')

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'start_datetime')
    def start_datetime(self):
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'end_datetime')
    def end_datetime(self):
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'location')
    def location(self):
        return None

InitializeClass(NewsItemReference)


class AgendaItemReference(NewsItemReference):
    grok.adapts(IAgendaItemContentVersion, Interface)

    security = ClassSecurityInfo()

    @Lazy
    def occurrence(self):
        occurrences = self.context.get_occurrences()
        if len(occurrences):
            return occurrences[0]
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'start_datetime')
    def start_datetime(self):
        if self.occurrence is not None:
            return self.occurrence.get_start_datetime()
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'end_datetime')
    def end_datetime(self):
        if self.occurrence is not None:
            return self.occurrence.get_end_datetime()
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'location')
    def location(self):
        if self.occurrence is not None:
            return self.occurrence.get_location()
        return None


InitializeClass(AgendaItemReference)


class RSSItemReference(object):
    """a temporary object to wrap a newsitem"""
    grok.implements(INewsItemReference)

    security = ClassSecurityInfo()

    def __init__(self, item, context, request):
        self._item = item
        self._context = context
        self._request = request

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'id')
    def id(self):
        return self._item['title']

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'title')
    def title(self):
        return self._item['title']

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'description')
    def description(self, maxchars=1024):
        # XXX we're not so sure about the type of content, so let's not
        # try to limit it for now...
        return self._item['description']

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'link')
    def link(self):
        return self._item['link']

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'thumbnail')
    def thumbnail(self):
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'introduction')
    def introduction(self, maxchars=1024):
        return self.description(maxchars)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'creation_datetime')
    def creation_datetime(self):
        return (self._toDateTime(self._item.get('created')) or
                self._toDateTime(self._item.get('date')) or None)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'start_datetime')
    def start_datetime(self):
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'end_datetime')
    def end_datetime(self):
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'location')
    def location(self):
        return getattr(self._item, 'location', None)

    def _toDateTime(self, dt):
        """converts a Python datetime object to a localized Zope
           DateTime one"""
        if dt is None:
            return None
        if type(dt) in [str, unicode]:
            # string
            dt = DateTime(dt)
            return dt.toZone(dt.localZone())
        elif type(dt) == tuple:
            # tuple
            return DateTime(*dt)
        # datetime?
        return DateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute)


InitializeClass(AgendaItemReference)


class RSSAggregatorNewsProvider(grok.Adapter):
    grok.implements(INewsProvider)
    grok.context(IRSSAggregator)

    def get_items(self, request, number):
        """return a number of the most current items

            note that this may return less than number, since the RSS feed
            might not provide enough items
        """
        items = self.context.get_merged_feed_contents()
        for item in items[:number]:
            info = RSSItemReference(item, self.context, request)
            info.__parent__ =  self.context
            yield info


module_security.declarePublic('get_items')
def get_items(viewer, request, limit):
    return list(INewsProvider(viewer).get_items(request, limit))
