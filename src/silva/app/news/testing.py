# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.testing import SilvaLayer
import transaction
import silva.app.news


class SilvaNewsLayer(SilvaLayer):
    default_packages = SilvaLayer.default_packages + [
        'silva.core.editor',
        'silva.app.news'
        ]

    def _install_application(self, app):
        super(SilvaNewsLayer, self)._install_application(app)
        app.root.service_extensions.install('silva.app.news')
        transaction.commit()


FunctionalLayer = SilvaNewsLayer(silva.app.news)
