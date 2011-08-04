# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: newsprovider.py,v 1.3 2005/05/02 14:22:52 guido Exp $
#
from AccessControl import ModuleSecurityInfo

from DateTime import DateTime
from five import grok
from silva.app.document.interfaces import IDocumentDetails
from silva.app.news.interfaces import IAgendaItemVersion
from silva.app.news.interfaces import INewsViewer, IAggregator
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.traversing.browser import absoluteURL


module_security = ModuleSecurityInfo('silva.app.news.codesources.inline')


class INewsProvider(Interface):
    """is able to provide news items"""

    def get_items(self, number, request):
        """returns a set of the most current items"""


class INewsItemReference(Interface):

    def id(self):
        """get the ID of this reference"""

    def title(self):
        """get the title of this reference"""

    def description(self, maxchars):
        """get the description (from metadata) of this reference"""

    def thumbnail(self):
        """get the thumbnail"""

    def introduction(self, maxchars):
        """get the intro of this reference"""

    def link(self):
        """get the link(url) of this reference"""

    def creation_datetime(self):
        """get the creationdatetime of this reference"""

    def start_datetime(self):
        """get the sdt of this reference"""

    def end_datetime(self):
        """get the edt of this reference"""

    def location(self):
        """get the  of this reference"""


class NewsViewerNewsProvider(grok.Adapter):
    """Works for BOTH News and Agenda Viewers!"""
    grok.context(INewsViewer)
    grok.implements(INewsProvider)

    def get_items(self, request, number):
        results = self.context.get_items()
        for item in results[:number]:
            newsitem = item.get_viewable()
            if newsitem is None:
                continue
            yield NewsItemReference(newsitem, self.context, request)


class NewsItemReference(object):
    """a temporary object to wrap a newsitem"""
    grok.implements(INewsItemReference)

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, item, context, request):
        self._item = item
        self._context = context
        self._request = request
        self._details = queryMultiAdapter(
            (self._item, self._request), IDocumentDetails)

    def id(self):
        return self._item.id

    def title(self):
        return self._item.get_title()

    def description(self, maxchars=1024):
        # we can be sure there is no markup here, so just limit
        desc = self._item.get_description()
        if desc is None:
            return ''
        if maxchars > 0:
          desc = desc[:maxchars]
        return desc

    def link(self):
        return absoluteURL(self._item, self._request)

    def thumbnail(self):
        if self._details is not None:
            return self._details.get_thumbnail()
        return None

    def introduction(self, maxchars=1024):
        if self._details is not None:
            return self._details.get_introduction(length=maxchars)
        return None

    def creation_datetime(self):
        datetime = self._item.get_display_datetime()
        if datetime is not None:
            return datetime
        return self._context.service_metadata.getMetadataValue(
            self._item, 'silva-extra', 'publicationtime')

    def start_datetime(self):
        if IAgendaItemVersion.providedBy(self._item):
            return self._item.get_start_datetime()
        return None

    def end_datetime(self):
        if IAgendaItemVersion.providedBy(self._item):
            return self._item.get_end_datetime()
        return None

    def location(self):
        if IAgendaItemVersion.providedBy(self._item):
            return self._item.get_location()
        return None


class RSSItemReference(object):
    """a temporary object to wrap a newsitem"""
    grok.implements(INewsItemReference)

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, item, context, request):
        self._item = item
        self._context = context
        self._request = request

    def id(self):
        return self._item['title']

    def title(self):
        return self._item['title']

    def description(self, maxchars=1024):
        # XXX we're not so sure about the type of content, so let's not
        # try to limit it for now...
        return self._item['description']

    def link(self):
        return self._item['link']

    def thumbnail(self):
        return None

    def introduction(self, maxchars=1024):
        return self.description(maxchars)

    def creation_datetime(self):
        return (self._toDateTime(self._item.get('created')) or
                self._toDateTime(self._item.get('date')) or None)

    def start_datetime(self):
        return None

    def end_datetime(self):
        return None

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


class RSSAggregatorNewsProvider(grok.Adapter):
    grok.implements(INewsProvider)
    grok.context(IAggregator)

    def get_items(self, request, number):
        """return a number of the most current items

            note that this may return less than number, since the RSS feed
            might not provide enough items
        """
        items = self.context.get_merged_feed_contents()
        for item in items[:number]:
            yield RSSItemReference(item, self.context, request)


module_security.declarePublic('get_items')
def get_items(viewer, request, limit):
    return list(INewsProvider(viewer).get_items(request, limit))
