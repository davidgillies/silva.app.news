# Copyright (c) 2002-2006 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: newsprovider.py,v 1.3 2005/05/02 14:22:52 guido Exp $
#

import Globals
from AccessControl import ClassSecurityInfo
from DateTime import DateTime

from Products.Silva.adapters import adapter
from Products.SilvaNews.adapters import interfaces

from Products.Silva import SilvaPermissions

class NewsItemReference:
    """a temporary object to wrap a newsitem"""

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, item, context):
        self._item = item
        self._context = context

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
        return self._item.aq_parent.absolute_url()

    def intro(self, maxchars=1024):
        return self._item.get_intro(maxchars)
    
    def creation_datetime(self):
        creation_datetime = self._context.service_metadata.getMetadataValue(
                        self._item, 'silva-extra', 'creationtime')
        return creation_datetime

    def start_datetime(self):
        if hasattr(self._item, 'start_datetime'):
            return self._item.start_datetime()

    def end_datetime(self):
        if hasattr(self._item, 'end_datetime'):
            return self._item.end_datetime()

    def location(self):
        if hasattr(self._item, 'location'):
            return self._item.location()

Globals.InitializeClass(NewsItemReference)

class NewsViewerNewsProvider(adapter.Adapter):

    __implements__ = interfaces.INewsProvider

    def getitems(self, number):
        context = self.context
        context.verify_filters()
        results = []
        for newsfilter in context._filters:
            filterob = context.aq_inner.restrictedTraverse(newsfilter)
            res = filterob.get_last_items(number, False)
            results += res
        results = context._remove_doubles(results)
        ret = []
        for item in results[:number]:
            obj = item.getObject()
            ref = NewsItemReference(obj, self.context)
            ret.append(ref)
        return ret

class AgendaViewerNewsProvider(adapter.Adapter):

    __implements__ = interfaces.INewsProvider

    def getitems(self, number):
        context = self.context
        results = []
        for newsfilter in context._filters:
            # XXX this is the Nth time I'm copying this code, need to 
            # investigate some refactoring when I have some more time to
            # spare...
            filterob = context.aq_inner.restrictedTraverse(newsfilter)
            now = DateTime().earliestTime()
            # request everything until 1 year from now
            end = DateTime() + 366
            
            query1 = filterob._prepare_query(['Silva Agenda Item Version'])
            query1['sort_on'] = 'idx_end_datetime'
            query1['sort_order'] = 'ascending'
            query1['idx_end_datetime'] = (now, end)
            query1['idx_end_datetime_usage'] = 'range:min:max'
            res = filterob._query(**query1)
            
            query2 = filterob._prepare_query(['Silva Agenda Item Version'])
            query2['sort_on'] = 'idx_start_datetime'
            query2['sort_order'] = 'ascending'
            query2['idx_start_datetime'] = (now, end)
            query2['idx_start_datetime_usage'] = 'range:min:max'
            res += filterob._query(**query2)
            
            results += res
        # wrap and remove doubles
        ret = []
        paths = []
        for item in results[:number]:
            obj = item.getObject()
            path = obj.getPhysicalPath()
            if path not in paths:
                ref = NewsItemReference(obj, self.context)
                ret.append(ref)
                paths.append(path)
        return ret

class RSSItemReference:
    """a temporary object to wrap a newsitem"""

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, item, context):
        self._item = item
        self._context = context

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

    def intro(self, maxchars=1024):
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
        """converts a Python datetime object to a Zope DateTime one"""
        if dt is None:
            return None
        if type(dt) in [str, unicode]:
            # string
            return DateTime(dt)
        elif type(dt) == tuple:
            # tuple 
            return DateTime(*dt)
        # datetime?
        return DateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute)

Globals.InitializeClass(NewsItemReference)

class RSSAggregatorNewsProvider(adapter.Adapter):
    
    __implements__ = interfaces.INewsProvider

    def getitems(self, number):
        """return a number of the most current items

            note that this may return less than number, since the RSS feed
            might not provide enough items
        """
        items = self.context.get_merged_feed_contents()
        ret = []
        for item in items:
            ret.append(RSSItemReference(item, self.context))
        return ret[:number]

def getNewsProviderAdapter(context):
    if context.meta_type == 'Silva News Viewer':
        return NewsViewerNewsProvider(context)
    elif context.meta_type == 'Silva Agenda Viewer':
        return AgendaViewerNewsProvider(context) 
    elif context.meta_type == 'Silva RSS Aggregator':
        return RSSAggregatorNewsProvider(context)
