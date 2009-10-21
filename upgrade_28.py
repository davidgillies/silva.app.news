# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.upgrade.upgrade import BaseUpgrader


VERSION_B1='2.2b1'


class NewsPubIsPrivateUpgrader(BaseUpgrader):
    """ upgrade obj._is_private to snn-np-settings: is_private
    metadata set"""

    def upgrade(self, obj):
        if obj.__dict__.has_key('_is_private'):
            ip = obj._is_private
            del obj._is_private
            newip = 'no'
            if ip:
                newip = 'yes'
            binding = obj.service_metadata.getMetadata(obj)
            binding.setValues('snn-np-settings',{'is_private': newip})
        return obj


newspubupgrader = NewsPubIsPrivateUpgrader(
    VERSION_B1, 'Silva News Publication')


class IndexUpgrader(BaseUpgrader):
    """ remove the idx_is_private catalog index; it's
        not used anymore"""
    def upgrade(self, obj):
        if 'idx_is_private' in obj.service_catalog.indexes():
            obj.service_catalog.delIndex('idx_is_private')
        return obj


indexupgrader = IndexUpgrader(VERSION_B1, 'Silva Root')
