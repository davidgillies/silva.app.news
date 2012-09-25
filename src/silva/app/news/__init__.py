# -*- coding: utf-8 -*-
# Copyright (c) 2004-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.app.news.installer import install

from silva.core import conf as silvaconf

silvaconf.extension_name("silva.app.news")
silvaconf.extension_title("Silva News Network")
silvaconf.extension_depends(["Silva", "silva.app.document", "SilvaExternalSources"])


def initialize(context):
    from silva.app.news import indexing
    context.registerClass(
        indexing.IntegerRangesIndex,
        permission = 'Add Pluggable Index',
        constructors = (indexing.manage_addIntegerRangesIndexForm,
                        indexing.manage_addIntegerRangesIndex),
        visibility=None)


