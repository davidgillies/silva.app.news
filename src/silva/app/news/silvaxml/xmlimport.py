# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt


from Products.Silva.silvaxml import xmlimport
from Products.Silva.silvaxml.xmlimport import (
    SilvaBaseHandler, updateVersionCount)
from silva.core import conf as silvaconf
from silva.core.editor.transform.silvaxml import NS_EDITOR_URI
from silva.core.editor.transform.silvaxml.xmlimport import TextHandler

from five import grok
from silva.app.news.silvaxml import NS_NEWS_URI
from silva.app.news.silvaxml import helpers
from silva.app.news.datetimeutils import get_timezone

silvaconf.namespace(NS_NEWS_URI)


class NewsItemHandler(SilvaBaseHandler):
    grok.name('news_item')

    def getOverrides(self):
        return {(xmlimport.NS_SILVA_URI, 'content'): NewsItemVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, 'news_item'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addNewsItem(uid, '', no_default_version=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, 'news_item'):
            self.notifyImport()


class NewsItemVersionBodyHandler(xmlimport.SilvaBaseHandler):

    def getOverrides(self):
        return {(NS_EDITOR_URI, 'text'): TextHandler}

    def startElementNS(self, name, qname, attrs):
        if (NS_NEWS_URI, 'body') == name:
            self.setResult(self.parent().body)

    def endElementNS(self, name, qname):
        pass


class NewsItemVersionHandler(SilvaBaseHandler):
    grok.baseclass()

    def getOverrides(self):
        return {(NS_NEWS_URI, 'body'): NewsItemVersionBodyHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (xmlimport.NS_SILVA_URI, 'content'):
            uid = attrs[(None, 'version_id')].encode('utf-8')
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addNewsItemVersion(uid, '')
            self.setResultId(uid)

            version = self.result()
            helpers.set_as_list(version, 'target_audiences', attrs)
            helpers.set_as_list(version, 'subjects', attrs)
            helpers.set_as_naive_datetime(version, 'display_datetime', attrs)

    def endElementNS(self, name, qname):
        if name == (xmlimport.NS_SILVA_URI, 'content'):
            updateVersionCount(self)
            self.storeMetadata()
            self.storeWorkflow()


class AgendaItemHandler(SilvaBaseHandler):
    grok.name('agenda_item')

    def getOverrides(self):
        return {(xmlimport.NS_SILVA_URI, 'content'): AgendaItemVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, 'agenda_item'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addAgendaItem(uid, '', no_default_version=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, 'agenda_item'):
            self.notifyImport()


class AgendaItemVersionHandler(SilvaBaseHandler):
    grok.baseclass()

    def getOverrides(self):
        return {(NS_NEWS_URI, 'body'): NewsItemVersionBodyHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (xmlimport.NS_SILVA_URI, 'content'):
            uid = attrs[(None, 'version_id')].encode('utf-8')
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addAgendaItemVersion(uid, '')
            self.setResultId(uid)

            version = self.result()
            helpers.set_as_list(version, 'target_audiences', attrs)
            helpers.set_as_list(version, 'subjects', attrs)
            helpers.set(version, 'location', attrs)
            helpers.set(version, 'recurrence', attrs)
            tz_name = helpers.set(version, 'timezone_name', attrs)
            tz = None
            if tz_name:
                tz = get_timezone(tz_name)
            helpers.set_as_bool(version, 'all_day', attrs)
            helpers.set_as_datetime(version, 'start_datetime', attrs, tz=tz)
            helpers.set_as_datetime(version, 'end_datetime', attrs, tz=tz)
            helpers.set_as_naive_datetime(version, 'display_datetime', attrs)

    def endElementNS(self, name, qname):
        if name == (xmlimport.NS_SILVA_URI, 'content'):
            updateVersionCount(self)
            self.storeMetadata()
            self.storeWorkflow()


class NewsPublicationHandler(SilvaBaseHandler):
    grok.name('news_publication')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, grok.name.bind(self).get(self)):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addNewsPublication(uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, grok.name.bind(self).get(self)):
            self.storeMetadata()
            self.notifyImport()


class NewsViewerHandler(SilvaBaseHandler):
    """Import a defined News Viewer.
    """
    grok.name('news_viewer')

    def createViewer(self, uid, attrs):
        factory = self.parent().manage_addProduct['silva.app.news']
        factory.manage_addNewsViewer(uid, '')
        self.setResultId(uid)

        viewer = self.result()
        helpers.set_as_list(viewer, 'target_audiences', attrs)
        helpers.set_as_list(viewer, 'subjects', attrs)
        helpers.set_as_bool(viewer, 'number_is_days', attrs)
        helpers.set_as_int(viewer, 'number_to_show', attrs)
        helpers.set_as_int(viewer, 'number_to_show_archive', attrs)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, grok.name.bind(self).get(self)):
            uid = self.generateOrReplaceId(str(attrs[(None, 'id')]))
            self.createViewer(uid, attrs)

        if name == (NS_NEWS_URI, 'filter'):
            target = attrs[(None, 'target')]
            info = self.getInfo()
            info.addAction(
                xmlimport.resolve_path,
                [self.result().add_filter, info, target])

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, grok.name.bind(self).get(self)):
            self.storeMetadata()
            self.notifyImport()


class AgendaViewerHandler(NewsViewerHandler):
    """Import a defined Agenda Viewer.
    """
    grok.name('agenda_viewer')

    def createViewer(self, uid, attrs):
        factory = self.parent().manage_addProduct['silva.app.news']
        factory.manage_addAgendaViewer(uid, '')
        self.setResultId(uid)

        viewer = self.result()
        helpers.set_as_list(viewer, 'target_audiences', attrs)
        helpers.set_as_list(viewer, 'subjects', attrs)
        helpers.set_as_bool(viewer, 'number_is_days', attrs)
        helpers.set_as_int(viewer, 'number_to_show', attrs)
        helpers.set_as_int(viewer, 'number_to_show_archive', attrs)
        helpers.set_as_int(viewer, 'days_to_show', attrs)


class NewsFilterHandler(SilvaBaseHandler):
    grok.name('news_filter')

    def createFilter(self, uid, attrs):
        factory = self.parent().manage_addProduct['silva.app.news']
        factory.manage_addNewsFilter(uid, '')
        self.setResultId(uid)

        obj = self.result()
        helpers.set_as_list(obj, 'target_audiences', attrs)
        helpers.set_as_list(obj, 'subjects', attrs)
        helpers.set_as_bool(obj, 'show_agenda_items', attrs)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, grok.name.bind(self).get(self)):
            uid = self.generateOrReplaceId(str(attrs[(None, 'id')]))
            self.createFilter(uid, attrs)

        if name == (NS_NEWS_URI, 'source'):
            target = attrs[(None, 'target')]
            info = self.getInfo()
            info.addAction(
                xmlimport.resolve_path,
                [self.result().add_source, info, target])

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, grok.name.bind(self).get(self)):
            self.storeMetadata()
            self.notifyImport()


class AgendaFilterHandler(NewsFilterHandler):
    """Import an Agenda Filter.
    """
    grok.name('agenda_filter')

    def createFilter(self, uid, attrs):
        factory = self.parent().manage_addProduct['silva.app.news']
        factory.manage_addAgendaFilter(uid, '')
        self.setResultId(uid)

        obj = self.result()
        helpers.set_as_list(obj, 'target_audiences', attrs)
        helpers.set_as_list(obj, 'subjects', attrs)


class RSSAggregatorHandler(SilvaBaseHandler):
    """Import a defined RSS Aggregator.
    """
    grok.name('rss_aggregator')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI,'rssaggregator'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addRSSAggregator(uid,'')
            self.setResultId(uid)

            obj = self.result()
            if (attrs.get((None, 'feed_urls'),None)):
                feed_urls = attrs[(None,'feed_urls')]
                # reformat feed_urls to be in the format set_feeds expects
                obj.set_feeds(feed_urls)

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, 'rss_aggregator'):
            self.storeMetadata()
            self.notifyImport()

