# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.31 $

"""Install and Uninstall for Silva News
"""

from zope import interface

from Products.Silva.fssite import manage_addDirectoryView
from Products.Silva.install import add_fss_directory_view, add_helper, \
                                        py_add_helper

from Products.Silva.i18n import translate as _

try:
    from Products.Silva.interfaces import IInvisibleService
except ImportError:
    IInvisibleService = None

def install(root):
    """The view infrastructure for Silva.
    """
    # create the core views from filesystem
    # XXX this takes an inordinate amount of time..why?
    add_fss_directory_view(root.service_views, 'SilvaNews', __file__, 'views')
    # also register views
    registerViews(root.service_view_registry)

    # and editor
    configureXMLWidgets(root)

    # add and/or update catalog
    setup_catalog(root)

    # metadata
    setupMetadata(root)

    # tab security
    configureSecurity(root)

    # allowed_addables_in_publication
    configureAddables(root)

    # install some helper scripts in the root
##     configureLayout(root)

    # and add a service_news to the Silva root
    if not hasattr(root, 'service_news'):
        root.manage_addProduct['SilvaNews'].manage_addServiceNews(
            'service_news', 'Service for News')

def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['SilvaNews'])
    #delete the service_news_sub_editor/viewer widgets
    root.manage_delObjects(['service_news_sub_viewer'])
    #the editor isn't installed anymore, but remove it if it is installed
    if hasattr(root,'service_news_sub_editor'):
        root.manage_delObjects(['service_news_sub_editor'])
    unconfigureXMLWidgets(root)
    # The following line is commented out, so the service will remain installed
    # as an uninstall is performed. This will cause a Refresh action to leave
    # the service alone
    # root.manage_delObjects(['service_news'])

def is_installed(root):
    return hasattr(root.service_views, 'SilvaNews')

def registerViews(reg):
    """Register core views on registry.
    """
    # edit    
    reg.register('edit',
                 'Silva Agenda Filter', ['edit', 'Asset', 'Filter', 'AgendaFilter'])
    reg.register('edit',
                 'Silva News Filter', ['edit', 'Asset', 'Filter', 'NewsFilter'])
    reg.register('edit',
                 'Silva News Publication', ['edit', 'Container', 'NewsPublication'])
    reg.register('edit',
                 'Silva News Viewer', ['edit', 'Content', 'NewsViewer'])
    reg.register('edit',
                 'Silva RSS Aggregator', ['edit', 'Content', 'RSSAggregator'])
    reg.register('edit',
                 'Silva Agenda Viewer', ['edit', 'Content', 'AgendaViewer'])
    reg.register('edit',
                 'Silva Article', ['edit', 'VersionedContent', 'NewsItem', 'PlainArticle'])
    reg.register('edit',
                 'Silva Agenda Item', ['edit', 'VersionedContent', 'NewsItem', 'PlainAgendaItem'])
    reg.register('edit',
                 'Silva News Category Filter', ['edit', 'Asset', 'Filter', 'CategoryFilter'])

    # public
    reg.register('public',
                 'Silva Agenda Filter', ['public', 'AgendaFilter'])
    reg.register('public',
                 'Silva News Filter', ['public', 'NewsFilter'])
    reg.register('public', 'Silva News Publication', ['public', 'NewsPublication'])
    reg.register('public', 'Silva News Viewer', ['public', 'NewsViewer'])
    reg.register('public', 'Silva RSS Aggregator', ['public', 'RSSAggregator'])
    reg.register('public', 'Silva Agenda Viewer', ['public', 'AgendaViewer'])
    reg.register('public', 'Silva Article Version', ['public', 'PlainArticle'])
    reg.register('public', 'Silva Agenda Item Version', ['public', 'PlainAgendaItem'])
    reg.register('public', 'Silva News Category Filter', ['public', 'CategoryFilter'])
    # register also the VersionedContent objects of the articles to allow
    # accessing the objects with an explicit /public/ URL part
    reg.register('public', 'Silva Article', ['public', 'PlainArticle'])
    reg.register('public', 'Silva Agenda Item', ['public', 'PlainAgendaItem'])

    # preview - required for e.g. the compare versions feature
    reg.register('preview', 'Silva Article Version', ['public', 'PlainArticle'])
    reg.register('preview', 'Silva Agenda Item Version', ['public', 
                                                          'PlainAgendaItem'])
    
    # add
    reg.register('add', 'Silva Agenda Filter', ['add', 'AgendaFilter'])
    reg.register('add', 'Silva News Filter', ['add', 'NewsFilter'])
    reg.register('add', 'Silva News Publication', ['add', 'NewsPublication'])
    reg.register('add', 'Silva News Viewer', ['add', 'NewsViewer'])
    reg.register('add', 'Silva RSS Aggregator', ['add', 'RSSAggregator'])
    reg.register('add', 'Silva Agenda Viewer', ['add', 'AgendaViewer'])
    reg.register('add', 'Silva Article', ['add', 'NewsItem', 'PlainArticle'])
    reg.register('add', 'Silva Agenda Item', ['add', 'NewsItem', 'PlainAgendaItem'])
    reg.register('add', 'Silva News Category Filter', ['add', 'CategoryFilter'])
    reg.register('add', 'Silva News Category Filter', ['add', 'CategoryFilter'])

def unregisterViews(reg):
    """Unregister core views on registry.
    """
    # edit
    reg.unregister('edit', 'Silva Agenda Filter')
    reg.unregister('edit', 'Silva News Filter')
    reg.unregister('edit', 'Silva News Publication')
    reg.unregister('edit', 'Silva News Viewer')
    reg.unregister('edit', 'Silva RSS Aggregator')
    reg.unregister('edit', 'Silva Agenda Viewer')
    reg.unregister('edit', 'Silva Article')
    reg.unregister('edit', 'Silva Agenda Item')
    reg.unregister('edit', 'Silva News Category Filter')
    # public
    reg.unregister('public', 'Silva Agenda Filter')
    reg.unregister('public', 'Silva News Filter')
    reg.unregister('public', 'Silva News Publication')
    reg.unregister('public', 'Silva News Viewer')
    reg.unregister('public', 'Silva RSS Aggregator')
    reg.unregister('public', 'Silva Agenda Viewer')
    reg.unregister('public', 'Silva Article Version')
    reg.unregister('public', 'Silva Agenda Item Version')
    # add
    reg.unregister('add', 'Silva Agenda Filter')
    reg.unregister('add', 'Silva News Filter')
    reg.unregister('add', 'Silva News Publication')
    reg.unregister('add', 'Silva News Viewer')
    reg.unregister('add', 'Silva RSS Aggregator')
    reg.unregister('add', 'Silva Agenda Viewer')
    reg.unregister('add', 'Silva Article')
    reg.unregister('add', 'Silva Agenda Item')
    reg.unregister('add', 'Silva News Category Filter')

def configureXMLWidgets(root):
    """Configure XMLWidgets registries, editor, etc'
    """
    # create the services for XMLWidgets
    for name in ['service_news_sub_viewer']:
        if not hasattr(root, name):
            root.manage_addProduct['XMLWidgets'].manage_addWidgetRegistry(name)

    if IInvisibleService is not None:
            interface.directlyProvides(
                root['service_news_sub_viewer'],
                IInvisibleService,
                *interface.directlyProvidedBy(root['service_news_sub_viewer']))

    # now register all widgets
    registerNewsSubViewer(root)

def unconfigureXMLWidgets(root):
    if hasattr(root.aq_explicit, 'service_news_sub_viewer'):
        root.manage_delObjects(['service_news_sub_viewer'])
    if hasattr(root.aq_explicit, 'service_news_sub_editor'):
        root.manage_delObjects(['service_news_sub_editor'])

def registerNewsSubViewer(root):
    wr = root.service_news_sub_viewer
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'field', 'mode_view'))

    for name in ['p', 'list', 'heading', 'pre', 'toc', 'image',
                 'nlist', 'table', 'dlist', 'code', 'cite']:
        wr.addWidget(
            name,
            ('service_widgets', 'element', 'doc_elements', name, 'mode_view'))

def setup_catalog(silva_root):
    """Sets the ZCatalog up"""
    catalog = silva_root.service_catalog

    #object_path is the Content Object path (parent)
    #of Version objects (e.g. PlainNewsArticleVersion).
    columns = ['object_path','end_datetime','start_datetime','location','get_title', 'display_datetime','get_intro']
    #will need to add: external_link, link_method
    #                  subjects, target_audiences, teaser
    # , formatEventSummary (need to determine how to integrate "my"
    #     event intro and get_intro

    indexes = [
        ('idx_is_private', 'FieldIndex'),
        ('object_path', 'FieldIndex'),
        ('idx_parent_path', 'FieldIndex'),
        ('idx_start_datetime', 'DateIndex'),
        ('idx_end_datetime', 'DateIndex'),
        ('idx_display_datetime', 'DateIndex'),
        ('idx_subjects', 'KeywordIndex'),
        ('idx_target_audiences', 'KeywordIndex'),
        ]

    existing_columns = catalog.schema()
    existing_indexes = catalog.indexes()

    for column_name in columns:
        if column_name in existing_columns:
            continue
        catalog.addColumn(column_name)

    for field_name, field_type in indexes:
        if field_name in existing_indexes:
            continue
        if field_type == 'ZCTextIndex':
            extra = RecordStyle(
                {'doc_attr':field_name,
                 'lexicon_id':'silva_lexicon',
                 'index_type':'Okapi BM25 Rank'}
                )
            catalog.addIndex(field_name, field_type, extra)
        else:
            catalog.addIndex(field_name, field_type)

def setupMetadata(root):
    mapping = root.service_metadata.getTypeMapping()
    default = ''
    tm = (
            {'type': 'Silva Agenda Filter', 'chain': 'silva-content, silva-extra'},
            {'type': 'Silva News Filter', 'chain': 'silva-content, silva-extra'},
            {'type': 'Silva News Publication', 'chain': 'silva-content, silva-extra'},
            {'type': 'Silva News Viewer', 'chain': 'silva-content, silva-extra'},
            {'type': 'Silva RSS Aggregator', 'chain': 'silva-content, silva-extra'},
            {'type': 'Silva Agenda Viewer', 'chain': 'silva-content, silva-extra'},
            {'type': 'Silva Article Version', 'chain': 'silva-content, silva-extra'},
            {'type': 'Silva Agenda Item Version', 'chain': 'silva-content, silva-extra'},
            {'type': 'Silva News Category Filter', 'chain': 'silva-content, silva-extra'},
        )
        
    mapping.editMappings(default, tm)

def configureSecurity(root):
    all_author = ['Author', 'Editor', 'ChiefEditor', 'Manager']
    
    add_permissions = [
        'Add Silva Agenda Filters',
        'Add Silva Agenda Item Versions',
        'Add Silva Agenda Items',
        'Add Silva Agenda Viewers',
        'Add Silva Article Versions',
        'Add Silva Articles',
        'Add Silva News Filters',
        'Add Silva News Publications',
        'Add Silva News Viewers',
        'Add Silva RSS Aggregators',
        'Add Silva News Category Filters',
        ]

    for perm in add_permissions:
        root.manage_permission(perm, all_author)

def configureAddables(root):
    """Make sure the news items aren't addable in the root"""
    news_non_addables = ['Silva Article', 
                            'Silva Agenda Item',
                            ]
    news_addables = ['Silva Agenda Filter',
                        'Silva News Filter',
                        'Silva News Publication',
                        'Silva News Viewer',
                        'Silva RSS Aggregator',
                        'Silva Agenda Viewer',
                        'Silva News Category Filter',
                        ]
    current_addables = root.get_silva_addables_allowed_in_publication()
    new_addables = []
    for a in current_addables:
        if a not in news_non_addables:
            new_addables.append(a)
    for a in news_addables:
        if a not in new_addables:
            new_addables.append(a)
    root.set_silva_addables_allowed_in_publication(new_addables)

def configureLayout(root, default_if_existent=0):
    """Add some files to the root"""
    if not hasattr(root, 'rss.xml'):
        add_helper(root, 'rss.xml.py', globals(), py_add_helper, default_if_existent)

if __name__ == '__main__':
    print """This module is not an installer. You don't have to run it."""
