# -*- coding: utf-8 -*-
# Copyright (c) 2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging
from silva.core.upgrade.upgrade import BaseUpgrader
from silva.core.services.interfaces import ICataloging

logger = logging.getLogger('silva.app.news')

VERSION_301 = '3.0.1'

class RootUpgrader(BaseUpgrader):
    """
        Since we're changing the timestamp_ranges index
        from 32bits to 64bits, we need to recreate it.
    """

    def upgrade(self, root):
        # Update timestamp_ranges index
        catalog = root.service_catalog
        catalog_indexes = catalog.indexes()

        if 'timestamp_ranges' in catalog_indexes:
            catalog.delIndex('timestamp_ranges')
            catalog.addIndex('timestamp_ranges', 'IntegerRangesIndex')

        return root

root_upgrader = RootUpgrader(VERSION_301, 'Silva Root')


class Reindex(BaseUpgrader):
    """
        Recurring agenda newsitems are indexed in timestamp_ranges index
        this index went from 32 to 64bit - therefore associated
        content needs to be reindexed.
    """

    def upgrade(self, item):
        ICataloging(item).reindex()

        return item

news_item_reindexer   = Reindex(VERSION_301, 'Silva News Item')
agenda_item_reindexer = Reindex(VERSION_301, 'Silva Agenda Item')
