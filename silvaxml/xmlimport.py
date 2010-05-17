# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.silvaxml.xmlimport import (
    theXMLImporter, SilvaBaseHandler, NS_URI,
    generateUniqueId, updateVersionCount)
from Products.Silva import mangle
from silva.core import conf as silvaconf

from Products.SilvaDocument.silvaxml.xmlimport import (
    DOC_NS_URI, DocElementHandler)
from Products.SilvaNews.silvaxml.xmlexport import NS_SILVA_NEWS
from Products.SilvaNews.PlainArticle import (
    PlainArticle, PlainArticleVersion)
from Products.SilvaNews.PlainAgendaItem import (
    PlainAgendaItem, PlainAgendaItemVersion)


silvaconf.namespace(NS_SILVA_NEWS)


class SNNHandlerMixin(object):
    """ mixin class to handle shared attribute setting across
        many of the SNN objects """

    def set_attrs(self,attrs,obj):
        if attrs.has_key((None,'target_audiences')):
            tas = attrs[(None,'target_audiences')]
            obj.set_target_audiences(tas.split(','))
        if attrs.has_key((None,'subjects')):
            subjects = attrs[(None,'subjects')]
            obj.set_subjects(subjects.split(','))
        if attrs.has_key((None,'excluded_items')):
            eis = attrs[(None,'excluded_items')]
            for ei in eis.split(','):
                obj.set_excluded_item(ei,True)
        if attrs.has_key((None,'sources')):
            sources = attrs[(None,'sources')]
            for source in sources.split(','):
                obj.add_source(source,True)
        if attrs.has_key((None,'show_agenda_items')):
            show_agendas = attrs[(None,'show_agenda_items')]
            obj.set_show_agenda_items(show_agendas=='True')
        if attrs.has_key((None,'keep_to_path')):
            keep_to_path = attrs[(None,'keep_to_path')]
            obj.set_keep_to_path(keep_to_path=='True')
        if attrs.has_key((None,'number_to_show')):
            number_to_show = attrs[(None,'number_to_show')]
            obj.set_number_to_show(int(number_to_show))
        if attrs.has_key((None,'number_to_show_archive')):
            number_to_show_archive = attrs[(None,'number_to_show_archive')]
            obj.set_number_to_show_archive(int(number_to_show_archive))
        if attrs.has_key((None,'number_is_days')):
            number_is_days = attrs[(None,'number_is_days')]
            obj.set_number_is_days(number_to_show=='True')
        if attrs.has_key((None,'days_to_show')):
            days_to_show = attrs[(None,'days_to_show')]
            obj.set_days_to_show(int(days_to_show))
        if attrs.has_key((None,'filters')):
            filters = attrs[(None,'filters')]
            for f in filters.split(','):
                obj.set_filter(f,True)


class NewsItemElementHandler(DocElementHandler):
    silvaconf.baseclass()

    def startElementNS(self, name, qname, attrs):
        if name == (DOC_NS_URI, 'doc'):
            self._node = self._parent.content._content.documentElement
            self._tree = self._parent.content._content
        else:
            child = self._tree.createElement(name[1])
            self._node.appendChild(child)
            self._node = child
        for ns, attr in attrs.keys():
            self._node.setAttribute(attr, attrs[(ns, attr)])


class PlainArticleHandler(SilvaBaseHandler):
    silvaconf.name('plainarticle')

    def getOverrides(self):
        return {(NS_URI, 'content'): PlainArticleContentHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_NEWS, 'plainarticle'):
            id = attrs[(None, 'id')].encode('utf-8')
            uid = self.generateOrReplaceId(id)
            object = PlainArticle(uid)
            self.parent()._setObject(uid, object)
            self.setResult(getattr(self._parent, uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_NEWS, 'plainarticle'):
            self.result().indexVersions()


class PlainAgendaItemHandler(SilvaBaseHandler):
    silvaconf.name('plainagendaitem')

    def getOverrides(self):
        return {(NS_URI, 'content'): PlainAgendaItemContentHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_NEWS, 'plainagendaitem'):
            id = attrs[(None, 'id')].encode('utf-8')
            uid = self.generateOrReplaceId(id)
            object = PlainAgendaItem(uid)
            self.parent()._setObject(uid, object)
            self.setResult(getattr(self._parent, uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_NEWS, 'plainagendaitem'):
            self.result().indexVersions()


class PlainAgendaItemContentHandler(SilvaBaseHandler):
    silvaconf.baseclass()

    def getOverrides(self):
        return{(DOC_NS_URI, 'doc'): NewsItemElementHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            id = attrs[(None, 'version_id')].encode('utf-8')
            if not mangle.Id(self._parent, id).isValid():
                return
            version = PlainAgendaItemVersion(id)
            self.parent()._setObject(id, version)

            if attrs.has_key((None,'target_audiences')):
                tas = attrs[(None,'target_audiences')]
                version.set_target_audiences(tas.split(','))
            if attrs.has_key((None,'subjects')):
                subjects = attrs[(None,'subjects')]
                version.set_subjects(subjects.split(','))

            self.setResult(getattr(self._parent, id))
            updateVersionCount(self)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            self.setMaintitle()
            self.storeMetadata()
            self.storeWorkflow()


class PlainArticleContentHandler(SilvaBaseHandler):
    silvaconf.baseclass()

    def getOverrides(self):
        return{(DOC_NS_URI, 'doc'): NewsItemElementHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            id = attrs[(None, 'version_id')].encode('utf-8')
            if not mangle.Id(self._parent, id).isValid():
                return
            version = PlainArticleVersion(id)
            self.parent()._setObject(id, version)

            if attrs.has_key((None,'target_audiences')):
                tas = attrs[(None,'target_audiences')]
                version.set_target_audiences(tas.split(','))
            if attrs.has_key((None,'subjects')):
                subjects = attrs[(None,'subjects')]
                version.set_subjects(subjects.split(','))
            self.setResult(getattr(self._parent, id))
            updateVersionCount(self)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            self.setMaintitle()
            self.storeMetadata()
            self.storeWorkflow()


class NewsPublicationHandler(SilvaBaseHandler):
    silvaconf.name('newspublication')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_NEWS, 'newspublication'):
            id = str(attrs[(None, 'id')])
            parent = self.parent()
            if self.settings().replaceObjects() and id in parent.objectIds():
                self.setResult(getattr(parent, id))
                return
            uid = generateUniqueId(id, parent)
            factory = self.parent().manage_addProduct['SilvaNews']
            factory.manage_addNewsPublication(uid, '', create_default=0)
            self.setResult(getattr(parent, uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_NEWS, 'newspublication'):
            self.setMaintitle()
            self.storeMetadata()


class AgendaViewerHandler(SNNHandlerMixin, SilvaBaseHandler):
    """Import a defined Agenda Viewer.
    """
    silvaconf.name('agendaviewer')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_NEWS,'agendaviewer'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            factory = self.parent().manage_addProduct['SilvaNews']
            factory.manage_addAgendaViewer(uid,'')
            obj = getattr(self.parent(),uid)
            self.set_attrs(attrs,obj)
            self.setResult(getattr(self.parent(), uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_NEWS, 'agendaviewer'):
            self.setMaintitle()
            self.storeMetadata()


class NewsViewerHandler(SNNHandlerMixin, SilvaBaseHandler):
    """Import a defined News Viewer.
    """
    silvaconf.name('newsviewer')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_NEWS,'newsviewer'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            factory = self.parent().manage_addProduct['SilvaNews']
            factory.manage_addNewsViewer(uid,'')
            obj = getattr(self.parent(),uid)
            self.set_attrs(attrs,obj)
            self.setResult(getattr(self.parent(), uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_NEWS, 'newsviewer'):
            self.setMaintitle()
            self.storeMetadata()


class AgendaFilterHandler(SNNHandlerMixin, SilvaBaseHandler):
    """Import an Agenda Filter.
    """
    silvaconf.name('agendafilter')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_NEWS,'agendafilter'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            factory = self.parent().manage_addProduct['SilvaNews']
            factory.manage_addAgendaFilter(uid,'')
            obj = getattr(self.parent(),uid)
            self.set_attrs(attrs,obj)
            self.setResult(getattr(self.parent(), uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_NEWS, 'agendafilter'):
            self.setMaintitle()
            self.storeMetadata()


class NewsFilterHandler(SNNHandlerMixin, SilvaBaseHandler):
    silvaconf.name('newsfilter')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_NEWS,'newsfilter'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            factory = self.parent().manage_addProduct['SilvaNews']
            factory.manage_addNewsFilter(uid,'')
            obj = getattr(self.parent(),uid)
            self.set_attrs(attrs,obj)
            self.setResult(getattr(self.parent(), uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_NEWS, 'newsfilter'):
            self.setMaintitle()
            self.storeMetadata()


class CategoryFilterHandler(SNNHandlerMixin, SilvaBaseHandler):
    """Import a CategoryFilter.
    """
    silvaconf.name('categoryfilter')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_NEWS,'categoryfilter'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            factory = self.parent().manage_addProduct['SilvaNews']
            factory.manage_addCategoryFilter(uid,'')
            obj = getattr(self.parent(),uid)
            self.set_attrs(attrs,obj)
            self.setResult(getattr(self.parent(), uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_NEWS, 'categoryfilter'):
            self.setMaintitle()
            self.storeMetadata()


class RSSAggregatorHandler(SilvaBaseHandler):
    """Import a defined RSS Aggregator.
    """
    silvaconf.name('rssaggregator')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_NEWS,'rssaggregator'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            factory = self.parent().manage_addProduct['SilvaNews']
            factory.manage_addRSSAggregator(uid,'')
            obj = getattr(self.parent(),uid)
            if (attrs.get((None, 'feed_urls'),None)):
                feed_urls = attrs[(None,'feed_urls')]
                # reformat feed_urls to be in the format set_feeds expects
                feed_urls = '\n'.join(feed_urls.split(','))
                obj.set_feeds(feed_urls)
            self.setResult(getattr(self.parent(), uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_NEWS, 'rssaggregator'):
            self.setMaintitle()
            self.storeMetadata()


