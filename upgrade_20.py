# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.25 $
# zope imports
import zLOG

log_severity = zLOG.INFO

# silva imports
from Products.Silva.upgrade_140 import VERSION
from Products.Silva.upgrade import BaseUpgrader
from Products.ParsedXML.ParsedXML import ParsedXML
from silvaxmlattribute import SilvaXMLAttribute

# upgraders for SilvaNews-1.3 to SilvaNewsNetwork-2.0

class ContentConvertor(BaseUpgrader):
    """Convert ParsedXML content to SilvaXMLAttributes"""
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
cc_sav = ContentConvertor(VERSION, 'Silva Article Version')
cc_saiv = ContentConvertor(VERSION, 'Silva Agenda Item Version')

class Reindex(BaseUpgrader):
    """Reindex all news items after adding the new display_date metadata field
    
        This reindexing is an expensive operation!
    """
    
    def upgrade(self, silvaroot):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            "Reindexing news items - may take a while")
        catalog = silvaroot.service_catalog
        # we reindex more than we theoretically have to, because some problems
        # were reported with missing indexes after an upgrade
        catalog.reindexIndex('object_path', None)
        catalog.reindexIndex('idx_parent_path', None)
        catalog.reindexIndex('idx_start_datetime', None)
        catalog.reindexIndex('idx_end_datetime', None)
        catalog.reindexIndex('idx_display_datetime', None)
        catalog.reindexIndex('idx_subjects', None)
        catalog.reindexIndex('idx_target_audiences', None)
        return silvaroot
#reindexer = Reindex(VERSION, 'Silva Root')
