# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.13 $

"""Install and Uninstall for Silva News
"""

from Products.FileSystemSite.DirectoryView import manage_addDirectoryView
from Products.Silva.install import add_fss_directory_view

def install(root):
    """The view infrastructure for Silva.
    """
    # create the core views from filesystem
    add_fss_directory_view(root.service_views, 'SilvaNews', __file__, 'views')
    # also register views
    registerViews(root.service_view_registry)

    # and editor
    configureXMLWidgets(root)

    # add and/or update catalog
    setup_catalog(root)

    # and add a service_news to the Silva root
    root.manage_addProduct['SilvaNews'].manage_addServiceNews('service_news', 'Service for News')

def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['SilvaNews'])
    root.manage_delObjects(['service_news'])

def is_installed(root):
    return hasattr(root.service_views, 'SilvaNews')

def registerViews(reg):
    """Register core views on registry.
    """
    # edit
    reg.register('edit', 'Silva News AgendaFilter', ['edit', 'Filter', 'AgendaFilter'])
    reg.register('edit', 'Silva News NewsFilter', ['edit', 'Filter', 'NewsFilter'])
    reg.register('edit', 'Silva News NewsSource', ['edit', 'Container', 'NewsSource'])
    reg.register('edit', 'Silva News NewsViewer', ['edit', 'Content', 'NewsViewer'])
    reg.register('edit', 'Silva News AgendaViewer', ['edit', 'Content', 'AgendaViewer'])
    reg.register('edit', 'Silva News PlainArticle', ['edit', 'VersionedContent', 'NewsItem', 'PlainArticle'])
    reg.register('edit', 'Silva News PlainAgendaItem', ['edit', 'VersionedContent', 'NewsItem', 'PlainAgendaItem'])
    # public
    reg.register('public', 'Silva News AgendaFilter', ['public', 'AgendaFilter'])
    reg.register('public', 'Silva News NewsFilter', ['public', 'NewsFilter'])
    reg.register('public', 'Silva News NewsSource', ['public', 'NewsSource'])
    reg.register('public', 'Silva News NewsViewer', ['public', 'NewsViewer'])
    reg.register('public', 'Silva News AgendaViewer', ['public', 'AgendaViewer'])
    reg.register('public', 'Silva News PlainArticle', ['public', 'PlainArticle'])
    reg.register('public', 'Silva News PlainAgendaItem', ['public', 'PlainAgendaItem'])
    # add
    reg.register('add', 'Silva News AgendaFilter', ['add', 'AgendaFilter'])
    reg.register('add', 'Silva News NewsFilter', ['add', 'NewsFilter'])
    reg.register('add', 'Silva News NewsSource', ['add', 'NewsSource'])
    reg.register('add', 'Silva News NewsViewer', ['add', 'NewsViewer'])
    reg.register('add', 'Silva News AgendaViewer', ['add', 'AgendaViewer'])
    reg.register('add', 'Silva News PlainArticle', ['add', 'NewsItem', 'PlainArticle'])
    reg.register('add', 'Silva News PlainAgendaItem', ['add', 'NewsItem', 'PlainAgendaItem'])

def unregisterViews(reg):
    """Unregister core views on registry.
    """
    # edit
    reg.unregister('edit', 'Silva News AgendaFilter')
    reg.unregister('edit', 'Silva News NewsFilter')
    reg.unregister('edit', 'Silva News NewsSource')
    reg.unregister('edit', 'Silva News NewsViewer')
    reg.unregister('edit', 'Silva News AgendaViewer')
    reg.unregister('edit', 'Silva News PlainArticle')
    reg.unregister('edit', 'Silva News PlainAgendaItem')
    # public
    reg.unregister('public', 'Silva News AgendaFilter')
    reg.unregister('public', 'Silva News NewsFilter')
    reg.unregister('public', 'Silva News NewsSource')
    reg.unregister('public', 'Silva News NewsViewer')
    reg.unregister('public', 'Silva News AgendaViewer')
    reg.unregister('public', 'Silva News PlainArticle')
    reg.unregister('public', 'Silva News PlainAgendaItem')
    # add
    reg.unregister('add', 'Silva News AgendaFilter')
    reg.unregister('add', 'Silva News NewsFilter')
    reg.unregister('add', 'Silva News NewsSource')
    reg.unregister('add', 'Silva News NewsViewer')
    reg.unregister('add', 'Silva News AgendaViewer')
    reg.unregister('add', 'Silva News PlainArticle')
    reg.unregister('add', 'Silva News PlainAgendaItem')

def configureXMLWidgets(root):
    """Configure XMLWidgets registries, editor, etc'
    """
    # create the services for XMLWidgets
    for name in ['service_news_sub_editor', 'service_news_sub_viewer']:
        if not hasattr(root, name):
            root.manage_addProduct['XMLWidgets'].manage_addWidgetRegistry(name)

    # now register all widgets
    registerNewsSubEditor(root)
    registerNewsSubViewer(root)

def registerNewsSubEditor(root):
    wr = root.service_news_sub_editor
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'field', 'mode_normal'))

    for nodeName in ['p', 'heading', 'list', 'pre', 'image', 'table', 'nlist', 'dlist']:
        wr.addWidget(nodeName,
                     ('service_widgets', 'element', 'doc_elements', nodeName, 'mode_normal'))

    wr.setDisplayName('p', 'Paragraph')
    wr.setDisplayName('heading', 'Heading')
    wr.setDisplayName('list', 'List')
    wr.setDisplayName('pre', 'Preformatted')
    wr.setDisplayName('toc', 'Table of contents')
    wr.setDisplayName('image', 'Image')
    wr.setDisplayName('table', 'Table')
    wr.setDisplayName('nlist', 'Complex list')
    wr.setDisplayName('dlist', 'Definition list')

    wr.setAllowed('doc', ['p', 'heading', 'list', 'pre', 'nlist', 'table', 'image', 'dlist'])

def registerNewsSubViewer(root):
    wr = root.service_news_sub_viewer
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'field', 'mode_view'))

    for name in ['p', 'list', 'heading', 'pre', 'image', 'nlist', 'table', 'dlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements', name, 'mode_view'))

def setup_catalog(silva_root):
    """Sets the ZCatalog up"""
    if hasattr(silva_root, 'service_catalog'):
        catalog = silva_root.service_catalog
        if hasattr(catalog, 'UnicodeVocabulary'):
            catalog.manage_delObjects(['UnicodeVocabulary'])
    else:
        silva_root.manage_addProduct['ZCatalog'].manage_addZCatalog('service_catalog', 'Silva Service Catalog')
        catalog = silva_root.service_catalog

    catalog.manage_addProduct['ZCatalog'].manage_addVocabulary('UnicodeVocabulary', 'UnicodeVocabulary', 1, 'UnicodeSplitter')

    columns = ['contact_info', 'container_comment', 'expiration_datetime', 'get_title_html',
            'id', 'location', 'meta_type', 'object_path', 'publication_datetime', 'source_path',
            'sec_get_last_author_info', 'start_datetime', 'subheader', 'subjects', 'summary',
            'target_audiences', 'title', 'version_status']

    indexes = [('creation_datetime', 'FieldIndex'), ('fulltext', 'TextIndex'), ('id', 'FieldIndex'),
            ('is_private', 'FieldIndex'), ('meta_type', 'FieldIndex'), ('object_path', 'KeywordIndex'),
            ('parent_path', 'FieldIndex'), ('path', 'PathIndex'), ('publication_datetime', 'FieldIndex'),
            ('source_path', 'FieldIndex'), ('start_datetime', 'FieldIndex'), ('subjects', 'KeywordIndex'),
            ('target_audiences', 'KeywordIndex'), ('version_status', 'FieldIndex')]

    existing_columns = catalog.schema()
    existing_indexes = catalog.indexes()

    for column_name in columns:
        if column_name in existing_columns:
            continue
        catalog.addColumn(column_name)

    for field_name, field_type in indexes:
        if field_name in existing_indexes:
            continue
        catalog.addIndex(field_name, field_type)

    # set the vocabulary of the fulltext-index to some Unicode aware one
    # (Should probably be ISO-8859-1, but that Splitter crashes Zope 2.5.1?!?)
    catalog.Indexes['fulltext'].manage_setPreferences('UnicodeVocabulary')

if __name__ == '__main__':
    print """This module is not an installer. You don't have to run it."""
