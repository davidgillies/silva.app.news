from Products.Silva.silvaxml.xmlimport import theXMLImporter, SilvaBaseHandler, NS_URI, generateUniqueId, updateVersionCount
from Products.Silva import mangle

from Products.SilvaNews.silvaxml.xmlexport import NS_SILVANEWS
from zLOG import LOG,INFO

def initializeXMLImportRegistry():
    """Initialize the global importer object.
    """
    importer = theXMLImporter
    importer.registerHandler((NS_SILVANEWS, 'rssaggregator'), RSSAggregatorHandler)
    importer.registerHandler((NS_SILVANEWS, 'categoryfilter'), CategoryFilterHandler)
    importer.registerHandler((NS_SILVANEWS, 'newsfilter'), NewsFilterHandler)
    importer.registerHandler((NS_SILVANEWS, 'agendafilter'), AgendaFilterHandler)

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
            keep_to_path = attrs[(None,'number_to_show')]
            obj.set_number_to_show(int(number_to_show))
        if attrs.has_key((None,'number_to_show_archive')):
            keep_to_path = attrs[(None,'number_to_show_archive')]
            obj.set_number_to_show_archive(int(number_to_show_archive))
        if attrs.has_key((None,'number_is_days')):
            keep_to_path = attrs[(None,'number_is_days')]
            obj.set_number_is_days(number_to_show=='True')
        if attrs.has_key((None,'filters')):
            filters = attrs[(None,'filters')]
            for filter in filters.split(','):
                pass
            #obj.add_source(source,True)
        
class NewsViewerHandler(SNNHandlerMixin,SilvaBaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVANEWS,'newsviewer'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            self.parent().manage_addProduct['SilvaNews'].manage_addNewsViewer(uid,'')
            obj = getattr(self.parent(),uid)
            self.set_attrs(attrs,obj)
            self.setResult(getattr(self.parent(), uid))
    def endElementNS(self, name, qname):
        if name == (NS_SILVANEWS, 'newsviewer'):
            self.setMaintitle()
            self.storeMetadata()
class AgendaFilterHandler(SNNHandlerMixin,SilvaBaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVANEWS,'agendafilter'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            self.parent().manage_addProduct['SilvaNews'].manage_addAgendaFilter(uid,'')
            obj = getattr(self.parent(),uid)
            self.set_attrs(attrs,obj)
            self.setResult(getattr(self.parent(), uid))
    def endElementNS(self, name, qname):
        if name == (NS_SILVANEWS, 'agendafilter'):
            self.setMaintitle()
            self.storeMetadata()

class NewsFilterHandler(SNNHandlerMixin,SilvaBaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVANEWS,'newsfilter'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            self.parent().manage_addProduct['SilvaNews'].manage_addNewsFilter(uid,'')
            obj = getattr(self.parent(),uid)
            self.set_attrs(attrs,obj)
            self.setResult(getattr(self.parent(), uid))
    def endElementNS(self, name, qname):
        if name == (NS_SILVANEWS, 'newsfilter'):
            self.setMaintitle()
            self.storeMetadata()

class CategoryFilterHandler(SNNHandlerMixin,SilvaBaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVANEWS,'categoryfilter'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            self.parent().manage_addProduct['SilvaNews'].manage_addCategoryFilter(uid,'')
            obj = getattr(self.parent(),uid)
            self.set_attrs(attrs,obj)
            self.setResult(getattr(self.parent(), uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVANEWS, 'categoryfilter'):
            self.setMaintitle()
            self.storeMetadata()

class RSSAggregatorHandler(SilvaBaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVANEWS,'rssaggregator'):
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            self.parent().manage_addProduct['SilvaNews'].manage_addRSSAggregator(uid,'')
            obj = getattr(self.parent(),uid)
            if (attrs.get((None, 'feed_urls'),None)):
                feed_urls = attrs[(None,'feed_urls')]
                #reformat feed_urls to be in the format set_feeds expects
                feed_urls = '\n'.join(feed_urls.split(','))
                obj.set_feeds(feed_urls)
            self.setResult(getattr(self.parent(), uid))

    def endElementNS(self, name, qname):
        if name == (NS_SILVANEWS, 'rssaggregator'):
            self.setMaintitle()
            self.storeMetadata()




