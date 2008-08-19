from Products.Silva.silvaxml.xmlimport import theXMLImporter, SilvaBaseHandler, NS_URI, generateUniqueId, updateVersionCount
from Products.Silva import mangle

from Products.SilvaNews.silvaxml.xmlexport import NS_SILVANEWS
from zLOG import LOG,INFO

def initializeXMLImportRegistry():
    """Initialize the global importer object.
    """
    importer = theXMLImporter
    importer.registerHandler((NS_SILVANEWS, 'rssaggregator'), RSSAggregatorHandler)

class RSSAggregatorHandler(SilvaBaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVANEWS,'rssaggregator'):
            LOG('starting rss aggregator',INFO,'rss aggregator')
            id = str(attrs[(None, 'id')])
            uid = self.generateOrReplaceId(id)
            self.parent().manage_addProduct['SilvaNews'].manage_addRSSAggregator(uid,'')
            obj = getattr(self.parent(),uid)
            if (attrs.get((None, 'feed_urls'),None)):
                feed_urls = attrs[(None,'feed_urls')]
                LOG('setting feeds',INFO,feed_urls)
                obj.set_feeds(feed_urls)


