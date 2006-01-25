# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.22 $

import AgendaFilter, NewsFilter, ServiceNews, InlineViewer
import NewsPublication, NewsViewer, AgendaViewer, RSSAggregator
import PlainArticle, PlainAgendaItem

from Products.Silva.fssite import registerDirectory
from Products.Silva.ExtensionRegistry import extensionRegistry
#from Products.Silva.upgrade import upgrade_registry
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
import install

from Products.SilvaExternalSources import ExternalSource
import os

def initialize(context):

    extensionRegistry.register(
        'SilvaNews', 'Silva News', context,
        [NewsPublication,
         NewsFilter, NewsViewer, PlainArticle,
         AgendaFilter, AgendaViewer, PlainAgendaItem,
         RSSAggregator],
        install, depends_on='SilvaDocument')

    context.registerClass(
        InlineViewer.InlineViewer,
        constructors = (InlineViewer.manage_addInlineViewerForm,
                        InlineViewer.manage_addInlineViewer),
        icon = os.path.join(
                os.path.abspath(
                    os.path.dirname(ExternalSource.__file__)
                ),
                'www/codesource.png')
        )

    context.registerClass(
        ServiceNews.ServiceNews,
        constructors = (ServiceNews.manage_addServiceNewsForm,
                        ServiceNews.manage_addServiceNews),
        icon="www/newsservice.gif"
        )

    registerDirectory('views', globals())

    # metadata
    for obj in [
        NewsPublication.NewsPublication,
        NewsFilter.NewsFilter, NewsViewer.NewsViewer,
        PlainArticle.PlainArticleVersion,
        AgendaFilter.AgendaFilter, AgendaViewer.AgendaViewer,
        PlainAgendaItem.PlainAgendaItemVersion,
        RSSAggregator.RSSAggregator,
        ]:
        registerTypeForMetadata(getattr(obj, 'meta_type'))
    
import dates
def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('dates',)

# declare a global upgrade registry to use for upgrading SilvaNews
from Products.Silva.upgrade import UpgradeRegistry
upgrade_registry = UpgradeRegistry()

# import the actual upgraders
import upgrade_13, upgrade_20

# set the software version, NOTE THAT THIS MUST BE UP-TO-DATE for
# the upgrade to work correctly!!
# use only major and minor version parts, upgrade shouldn't happen
# on patch-level updates
software_version = '2.0'
