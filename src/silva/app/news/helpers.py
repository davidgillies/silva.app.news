# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

# Helpers for cs inline news viewer

from AccessControl import ModuleSecurityInfo
import Products
from silva.core.views.interfaces import IVirtualSite
from silva.app.news.interfaces import IViewer

module_security = ModuleSecurityInfo('silva.app.news.helpers')

module_security.declarePublic('get_viewers')
def get_viewers(context, request):
    """returns a list of available viewers
        finds all viewers on this level
    """
    model = context or request.get('model')
    root = IVirtualSite(request).get_root()

    #determine which silva types are IViewers
    viewer_metatypes = []
    mts = Products.meta_types
    for mt in mts:
        if (mt.has_key('instance') and
            IViewer.implementedBy(mt['instance'])):
            viewer_metatypes.append(mt['name'])

    #this should get all viewers at this level or higher
    # (to the vhost root), not at the code sources level
    objects = []
    container = model.get_container()
    while container != root.aq_parent:
        objs = [(o.get_title(), o.id) for o in
                container.objectValues(viewer_metatypes)]
        objects.extend(objs)
        container = container.aq_parent
    return objects
