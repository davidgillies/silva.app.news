# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.9 $

import AgendaFilter, NewsFilter, ServiceNews
import NewsSource, NewsViewer, AgendaViewer, RSSViewer
import PlainArticle, PlainAgendaItem
from Products.PythonScripts.Utility import allow_module
from AccessControl import ModuleSecurityInfo
from Products.FileSystemSite.DirectoryView import registerDirectory
from Products.Silva.ExtensionRegistry import extensionRegistry
import install

def initialize(context):

    # Is this still required? I think this was meant for the non-zmi installer (might be needed for the catalog)
    #ModuleSecurityInfo('Products').declarePublic('SilvaNews')
    #ModuleSecurityInfo('Products.SilvaNews').declarePublic('install')
    #ModuleSecurityInfo('Products.SilvaNews.install').declarePublic('NewsInstaller')

    extensionRegistry.register(
        'SilvaNews', 'Silva News', context, [
        AgendaFilter, AgendaViewer, NewsFilter, NewsViewer, RSSViewer, NewsSource, PlainArticle, PlainAgendaItem],
        install, depends_on='Silva')

    context.registerClass(
        ServiceNews.ServiceNews,
        constructors = (ServiceNews.manage_addServiceNewsForm,
                        ServiceNews.manage_addServiceNews),
        icon="www/silvaresolution.gif"
        )

    registerDirectory('views', globals())


