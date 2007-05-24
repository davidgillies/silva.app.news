# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.25 $

from zope.interface import implements

from Products.SilvaNews import upgrade_registry

# zope imports
import zLOG
from BTrees.Length import Length
from Products.PluginIndexes.common.UnIndex import UnIndex

log_severity = zLOG.INFO

# silva imports
from Products.Silva.interfaces import IUpgrader

# upgraders for SilvaNewsNetwork 2.0(.x) to 2.1(.x)

class IndexUpgrader:
    """Actually this should be in Zope itself, as it fixes a Zope core issue

        In Zope 2.8.x there was an internal API change in the UnIndex class,
        a superclass of some ZCatalog Indexes. For this change (they added an
        attribute called '_length' to the code) no upgrader was provided in
        Zope itself, however. This upgrader tries to solve this problem.
    """

    implements(IUpgrader)

    def upgrade(self, silvaroot):
        zLOG.LOG(
            'SilvaNews', zLOG.INFO,
            "Upgrading ZCatalog Indexes")
        catalog = silvaroot.service_catalog
        for index in catalog.index_objects():
            self._migrate_length(index)
        return silvaroot
        
    def _migrate_length(self, obj):
        if not isinstance(obj, UnIndex):
            return obj
        if hasattr(obj, '_length'):
            zLOG.LOG(
                'SilvaNews', zLOG.INFO,
                'Skipping already upgraded index %s' % obj.id)
            return obj
        zLOG.LOG(
            'SilvaNews', zLOG.INFO, 
            "Upgrading index %s" % obj.id)
        obj._length = Length(len(obj._unindex))
        return obj

upgrade_registry.registerUpgrader(
    IndexUpgrader(), '2.1', 'Silva Root')
