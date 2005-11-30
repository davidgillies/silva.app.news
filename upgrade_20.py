from Products.SilvaNews import upgrade_registry

# python imports
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

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
        print type(obj.content.aq_base)
        s = StringIO()
        obj.content.documentElement.writeStream(s)
        xml = s.getvalue()
        obj.content = SilvaXMLAttribute('content')
        obj.content._content = ParsedXML('content', xml)
        return obj

upgrade_registry.registerUpgrader(
    ContentConvertor(), '2.0', 'Silva Article Version')
upgrade_registry.registerUpgrader(
    ContentConvertor(), '2.0', 'Silva Agenda Item Version')
