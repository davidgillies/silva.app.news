from Products.SilvaNews import upgrade_registry

# zope imports
import zLOG

log_severity = zLOG.INFO

# silva imports
from Products.Silva.interfaces import IUpgrader
from Products.ParsedXML.ParsedXML import ParsedXML
from silvaxmlattribute import SilvaXMLAttribute

# upgraders for SilvaNews-1.3 to SilvaNewsNetwork-2.0

class ContentConvertor:
    """Convert ParsedXML content to SilvaXMLAttributes"""
    __implements__ = IUpgrader

    def upgrade(self, obj):
        zLOG.LOG(
            'SilvaNews',
            log_severity,
            'Converting ParsedXML to SilvaXMLAttibute on %s' % 
                '/'.join(obj.getPhysicalPath())
            )
        if type(obj.content.aq_base) == SilvaXMLAttribute:
            zLOG.LOG('SilvaNews', log_severity, 'Already converted')
            return obj
        class MyStringIO:
            def __init__(self, s=''):
                self._buffer = [s]
            def write(self, s):
                if type(s) == unicode:
                    s = s.encode('UTF-8')
                self._buffer.append(s)
            def getvalue(self):
                return ''.join(self._buffer)
        s = MyStringIO()
        obj.content.documentElement.writeStream(s)
        xml = s.getvalue()
        obj.content = SilvaXMLAttribute('content')
        obj.content._content = ParsedXML('content', xml)
        return obj

upgrade_registry.registerUpgrader(
    ContentConvertor(), '2.0', 'Silva Article Version')
upgrade_registry.registerUpgrader(
    ContentConvertor(), '2.0', 'Silva Agenda Item Version')

class ReindexDisplayDateTime:
    """Reindex all news items after adding the new display_date metadata field
    
        This reindexing is an expensive operation!
    """
    
    __implements__ = IUpgrader
    
    def upgrade(self, silvaroot):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            "Reindex display date/time - may take a while")
        catalog = silvaroot.service_catalog
        catalog.reindexIndex('idx_display_datetime', None)
        return silvaroot

upgrade_registry.registerUpgrader(
    ReindexDisplayDateTime(), '1.3', 'Silva Root')
