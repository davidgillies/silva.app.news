# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt
#
from itertools import islice

from AccessControl import ModuleSecurityInfo
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime

from five import grok
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.component import getUtility
from zope.interface import Interface
from zope.traversing.browser import absoluteURL
from zope.cachedescriptors.property import Lazy
from zope.intid.interfaces import IIntIds

from Products.Silva import SilvaPermissions
from silva.core.interfaces import IOrderManager
from silva.core.services.interfaces import IMetadataService
from silva.app.document.interfaces import IDocumentDetails
from silva.app.news.interfaces import IAgendaItemContentVersion
from silva.app.news.interfaces import INewsItemContentVersion
from silva.app.news.interfaces import INewsItemReference
from silva.app.news.interfaces import INewsViewer, IRSSAggregator
from silva.app.news.interfaces import INewsPublication, INewsItem


module_security = ModuleSecurityInfo('silva.app.news.codesources.api')

class INewsProvider(Interface):
    """is able to provide news items"""

    def get_items(self, number, request):
        """returns a set of the most current items"""


class NewsPublicationNewsProvider(grok.Adapter):
    grok.context(INewsPublication)
    grok.implements(INewsProvider)

    def publication_items(self, request):
        # XXX:
        intids = getUtility(IIntIds)
        for id_ in IOrderManager(self.context).order:
            content = intids.queryObject(id_)
            if content is not None and INewsItem.providedBy(content):
                version = content.get_viewable()
                if version is not None:
                    info = getMultiAdapter(
                            (version, request),
                            INewsItemReference)
                    info.__parent__ = self.context
                    yield info

    def get_items(self, request, number):
        return list(islice(self.publication_items(request), number))


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


def memoize(call):
    # Cheap caching: Remenber previous calls into the _cache dict of
    # the class instance.
    _marker = object()

    def remenber(self):
        value = self._cache.get(call.func_name, _marker)
        if value is _marker:
            value = self._cache[call.func_name] = call(self)
        return value

    return remenber


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
        self._cache = {}

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'id')
    def id(self):
        return self.content.id

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'title')
    @memoize
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
    @memoize
    def link(self):
        return absoluteURL(self.content, self.request)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'image_url')
    @memoize
    def image_url(self):
        if self.details is not None:
            return self.details.get_image_url() or u''
        return u''

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'thumbnail_url')
    @memoize
    def thumbnail_url(self):
        if self.details is not None:
            return self.details.get_thumbnail_url() or u''
        return u''

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'thumbnail')
    @memoize
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
    def introduction(self, maxchars=1024, maxwords=None):
        if self.details is not None:
            return self.details.get_introduction(
                length=maxchars, words=maxwords)
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'creation_datetime')
    @memoize
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

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'target_audiences')
    @memoize
    def target_audiences(self):
        return self.context.get_target_audiences()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'subjects')
    @memoize
    def subjects(self):
        return self.context.get_subjects()


InitializeClass(NewsItemReference)


def _toDateTime(dt):
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
    @memoize
    def start_datetime(self):
        if self.occurrence is not None:
            return _toDateTime(self.occurrence.get_start_datetime())
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'end_datetime')
    @memoize
    def end_datetime(self):
        if self.occurrence is not None:
            return _toDateTime(self.occurrence.get_end_datetime())
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'location')
    @memoize
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
        SilvaPermissions.AccessContentsInformation, 'image_url')
    def image_url(self):
        return None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'thumbnail_url')
    def thumbnail_url(self):
        return None

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
        return (_toDateTime(self._item.get('created')) or
                _toDateTime(self._item.get('date')) or None)

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

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'target_audiences')
    def target_audiences(self):
        return set([])

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'subjects')
    def subjects(self):
        return set([])



InitializeClass(RSSItemReference)


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
