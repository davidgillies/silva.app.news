# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.13 $

import AgendaFilter, NewsFilter, ServiceNews
import NewsSource, NewsViewer, AgendaViewer, RSSViewer
import PlainArticle, PlainAgendaItem
from Products.PythonScripts.Utility import allow_module
from AccessControl import ModuleSecurityInfo
from Products.FileSystemSite.DirectoryView import registerDirectory
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.upgrade import upgrade_registry, upgrade_list_titles_in_parsed_xml 
import install

def initialize(context):

    # Is this still required? I think this was meant for the non-zmi installer (might be needed for the catalog)
    #ModuleSecurityInfo('Products').declarePublic('SilvaNews')
    #ModuleSecurityInfo('Products.SilvaNews').declarePublic('install')
    #ModuleSecurityInfo('Products.SilvaNews.install').declarePublic('NewsInstaller')

    extensionRegistry.register(
        'SilvaNews', 'Silva News', context, [
        NewsSource, PlainArticle, PlainAgendaItem, NewsFilter, AgendaFilter, NewsViewer, AgendaViewer, RSSViewer],
        install, depends_on='Silva')

    context.registerClass(
        ServiceNews.ServiceNews,
        constructors = (ServiceNews.manage_addServiceNewsForm,
                        ServiceNews.manage_addServiceNews),
        icon="www/silvaresolution.gif"
        )

    registerDirectory('views', globals())

# upgrade methods
def upgrade_newsitem(obj):
    for o in obj.objectValues():
        upgrade_list_titles_in_parsed_xml(o.content)

upgrade_registry.register('Silva News Article', upgrade_newsitem)
upgrade_registry.register('Silva News AgendaItem', upgrade_newsitem)
