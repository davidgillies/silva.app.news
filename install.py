"""Install and Uninstall for Silva Eur
"""

from Products.FileSystemSite.DirectoryView import manage_addDirectoryView

def install(root):
    """The view infrastructure for Silva.
    """
    # create the core views from filesystem
    manage_addDirectoryView(root.service_views,
                            'Products/SilvaNews/views', 'SilvaNews')
    # also register views
    registerViews(root.service_view_registry)

    # and editor
    configureXMLWidgets(root)

    # add and/or update catalog
    setup_catalog(root)

def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['SilvaNews'])

def is_installed(root):
    return hasattr(root.service_views, 'SilvaNews')

def registerViews(reg):
    """Register core views on registry.
    """
    # edit
    reg.register('edit', 'Silva AgendaFilter', ['edit', 'Filter', 'AgendaFilter'])
    reg.register('edit', 'Silva NewsFilter', ['edit', 'Filter', 'NewsFilter'])
    reg.register('edit', 'Silva NewsSource', ['edit', 'Container', 'NewsSource'])
    reg.register('edit', 'Silva NewsViewer', ['edit', 'Content', 'NewsViewer'])
    reg.register('edit', 'Silva AgendaViewer', ['edit', 'Content', 'AgendaViewer'])
    reg.register('edit', 'Silva News PlainArticle', ['edit', 'VersionedContent', 'NewsItem', 'PlainArticle'])
    reg.register('edit', 'Silva News PlainAgendaItem', ['edit', 'VersionedContent', 'NewsItem', 'PlainAgendaItem'])
    # public
    reg.register('public', 'Silva AgendaFilter', ['public', 'AgendaFilter'])
    reg.register('public', 'Silva NewsFilter', ['public', 'NewsFilter'])
    reg.register('public', 'Silva NewsSource', ['public', 'NewsSource'])
    reg.register('public', 'Silva NewsViewer', ['public', 'NewsViewer'])
    reg.register('public', 'Silva AgendaViewer', ['public', 'AgendaViewer'])
    reg.register('public', 'Silva News PlainArticle', ['public', 'PlainArticle'])
    reg.register('public', 'Silva News PlainAgendaItem', ['public', 'PlainAgendaItem'])
    # add
    reg.register('add', 'Silva AgendaFilter', ['add', 'AgendaFilter'])
    reg.register('add', 'Silva NewsFilter', ['add', 'NewsFilter'])
    reg.register('add', 'Silva NewsSource', ['add', 'NewsSource'])
    reg.register('add', 'Silva NewsViewer', ['add', 'NewsViewer'])
    reg.register('add', 'Silva AgendaViewer', ['add', 'AgendaViewer'])
    reg.register('add', 'Silva News PlainArticle', ['add', 'NewsItem', 'PlainArticle'])
    reg.register('add', 'Silva News PlainAgendaItem', ['add', 'NewsItem', 'PlainAgendaItem'])

def unregisterViews(reg):
    """Unregister core views on registry.
    """
    # edit
    reg.unregister('edit', 'Silva AgendaFilter')
    reg.unregister('edit', 'Silva NewsFilter')
    reg.unregister('edit', 'Silva NewsSource')
    reg.unregister('edit', 'Silva NewsViewer')
    reg.unregister('edit', 'Silva AgendaViewer')
    reg.unregister('edit', 'Silva News PlainArticle')
    reg.unregister('edit', 'Silva News PlainAgendaItem')
    # public
    reg.unregister('public', 'Silva AgendaFilter')
    reg.unregister('public', 'Silva NewsFilter')
    reg.unregister('public', 'Silva NewsSource')
    reg.unregister('public', 'Silva NewsViewer')
    reg.unregister('public', 'Silva AgendaViewer')
    reg.unregister('public', 'Silva News PlainArticle')
    reg.unregister('public', 'Silva News PlainAgendaItem')
    # add
    reg.unregister('add', 'Silva AgendaFilter')
    reg.unregister('add', 'Silva NewsFilter')
    reg.unregister('add', 'Silva NewsSource')
    reg.unregister('add', 'Silva NewsViewer')
    reg.unregister('add', 'Silva AgendaViewer')
    reg.unregister('add', 'Silva News PlainArticle')
    reg.unregister('add', 'Silva News PlainAgendaItem')

def configureXMLWidgets(root):
    """Configure XMLWidgets registries, editor, etc'
    """
    # create the core widgets from the filesystem
    #manage_addDirectoryView(root,
    #                        'Products/Silva/widgets', 'service_widgets')

    # create the editor service
    #root.manage_addProduct['XMLWidgets'].manage_addEditorService(
    #    'service_editor')
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

    columns = ['academic', 'chair', 'co_promoter', 'contact_info', 'container_comment', 'end_datetime', 'expiration_datetime', 'get_title_html',
            'id', 'info', 'lead', 'location', 'meta_type', 'object_path', 'pressheader', 'pressnote', 'promovendus',
            'promoter', 'publication_datetime', 'source_path', 'sec_get_last_author_info', 'speakers',
            'specific_contact_info', 'start_datetime', 'subheader', 'subjects', 'summary', 'target_audiences', 'title',
            'version_status']

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
