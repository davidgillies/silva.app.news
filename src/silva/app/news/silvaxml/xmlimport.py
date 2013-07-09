# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from silva.core import conf as silvaconf
from silva.core.editor.transform.silvaxml import NS_EDITOR_URI
from silva.core.editor.transform.silvaxml.xmlimport import TextHandler

from five import grok
from silva.app.news.silvaxml import NS_NEWS_URI
from silva.app.news.silvaxml import helpers
from silva.app.news.datetimeutils import get_timezone
from silva.app.news.AgendaItem import AgendaItemOccurrence
from silva.core.xml import handlers, NS_SILVA_URI

silvaconf.namespace(NS_NEWS_URI)


class NewsItemHandler(handlers.SilvaHandler):
    grok.name('news_item')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): NewsItemVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, 'news_item'):
            uid = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addNewsItem(uid, '', no_default_version=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, 'news_item'):
            self.notifyImport()


class NewsItemVersionBodyHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {(NS_EDITOR_URI, 'text'): TextHandler}

    def startElementNS(self, name, qname, attrs):
        if (NS_NEWS_URI, 'body') == name:
            self.setResult(self.parent().body)

    def endElementNS(self, name, qname):
        pass


class NewsItemVersionHandler(handlers.SilvaVersionHandler):
    grok.baseclass()

    def getOverrides(self):
        return {(NS_NEWS_URI, 'body'): NewsItemVersionBodyHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            uid = attrs[(None, 'version_id')].encode('utf-8')
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addNewsItemVersion(uid, '')
            self.setResultId(uid)

            version = self.result()
            helpers.set_as_list(version, 'target_audiences', attrs)
            helpers.set_as_list(version, 'subjects', attrs)
            helpers.set_as_naive_datetime(version, 'display_datetime', attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'content'):
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()


class AgendaItemHandler(handlers.SilvaHandler):
    grok.name('agenda_item')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): AgendaItemVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, 'agenda_item'):
            uid = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addAgendaItem(uid, '', no_default_version=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, 'agenda_item'):
            self.notifyImport()


class AgendaItemOccurrenceHandler(handlers.SilvaHandler):
    silvaconf.baseclass()

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, 'occurrence'):
            occurrence = AgendaItemOccurrence()
            helpers.set(occurrence, 'location', attrs)
            helpers.set(occurrence, 'recurrence', attrs)
            tz_name = helpers.set(occurrence, 'timezone_name', attrs)
            tz = None
            if tz_name:
                tz = get_timezone(tz_name)
            helpers.set_as_bool(occurrence, 'all_day', attrs)
            helpers.set_as_datetime(occurrence, 'start_datetime', attrs, tz=tz)
            helpers.set_as_datetime(occurrence, 'end_datetime', attrs, tz=tz)

            self.parentHandler().occurrences.append(occurrence)


class AgendaItemVersionHandler(handlers.SilvaVersionHandler):
    grok.baseclass()

    def getOverrides(self):
        return {(NS_NEWS_URI, 'body'): NewsItemVersionBodyHandler,
                (NS_NEWS_URI, 'occurrence'): AgendaItemOccurrenceHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            uid = attrs[(None, 'version_id')].encode('utf-8')
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addAgendaItemVersion(uid, '')
            self.setResultId(uid)

            version = self.result()
            helpers.set_as_list(version, 'target_audiences', attrs)
            helpers.set_as_list(version, 'subjects', attrs)
            helpers.set_as_naive_datetime(version, 'display_datetime', attrs)
            self.occurrences = []

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'content'):
            self.result().set_occurrences(self.occurrences)
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()


class NewsPublicationHandler(handlers.SilvaHandler):
    grok.name('news_publication')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, grok.name.bind(self).get(self)):
            uid = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addNewsPublication(uid, '', no_default_content=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, grok.name.bind(self).get(self)):
            self.storeMetadata()
            self.notifyImport()


class NewsViewerHandler(handlers.SilvaHandler):
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
            uid = self.generateIdentifier(attrs)
            self.createViewer(uid, attrs)

        if name == (NS_NEWS_URI, 'filter'):
            target = attrs[(None, 'target')]
            importer = self.getExtra()
            content = self.result()
            importer.resolveImportedPath(content, content.add_filter, target)

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


class NewsFilterHandler(handlers.SilvaHandler):
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
            uid = self.generateIdentifier(attrs)
            self.createFilter(uid, attrs)

        if name == (NS_NEWS_URI, 'source'):
            target = attrs[(None, 'target')]
            importer = self.getExtra()
            content = self.result()
            importer.resolveImportedPath(content, content.add_source, target)

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


class RSSAggregatorHandler(handlers.SilvaHandler):
    """Import a defined RSS Aggregator.
    """
    grok.name('rss_aggregator')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_NEWS_URI, 'rss_aggregator'):
            uid = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['silva.app.news']
            factory.manage_addRSSAggregator(uid,'')
            self.setResultId(uid)
            self.urls = []

        if name == (NS_NEWS_URI, 'url'):
            self.buffer = ''

    def characters(self, chars):
        if hasattr(self, 'buffer'):
            self.buffer += chars

    def endElementNS(self, name, qname):
        if name == (NS_NEWS_URI, 'url'):
            self.urls.append(self.buffer.strip())

        if name == (NS_NEWS_URI, 'rss_aggregator'):
            self.storeMetadata()
            aggregator = self.result()
            aggregator.set_feeds(self.urls)
            self.notifyImport()

