# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.25 $

from zope.interface import implements

from Products.SilvaNews import upgrade_registry
from Products.Silva import upgrade_160, upgrade

# zope imports
import zLOG

log_severity = zLOG.INFO

# silva imports
from Products.Silva.interfaces import IUpgrader

upgrade_registry.registerUpgrader(
    upgrade_160.CatalogRefresher(), '2.6', upgrade.AnyMetaType)
