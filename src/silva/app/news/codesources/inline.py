# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt
#

from AccessControl import ModuleSecurityInfo

import zope.deferredimport

module_security = ModuleSecurityInfo('silva.app.news.codesources.inline')
module_security.declarePublic('get_items')

zope.deferredimport.deprecated(
    'Please refresh your News viewer code source',
    get_items='silva.app.news.codesources.api:get_items')
