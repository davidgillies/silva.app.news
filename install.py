from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ModuleSecurityInfo
from Products.Silva import SilvaPermissions
from Globals import InitializeClass

class NewsInstaller:
    """Class to install SilvaNews on the client's machine.
    Since some private methods are to be called,
    this code has to be run off the filesystem.
    Note that since ModuleSecurity doesn't allow protection
    of methods, all method check for manager-status themselves.
    """
    def __init__(self, context, sroot):
        """Starts the full process"""
        if not 'Manager' in context.REQUEST.AUTHENTICATED_USER.getRoles():
            raise 'Unauthorized', 'You are not allowed to install Silva News'
        self.install_product(context, sroot)
        self.setup_catalog(context, sroot)

    def install_product(self, context, silva_root):
        """Installs the ZMI-stuff"""
        if not 'Manager' in context.REQUEST.AUTHENTICATED_USER.getRoles():
            raise 'Unauthorized', 'You are not allowed to install Silva News'

        # empty backupdir
        ids = context.backup.objectIds()
        context.backup.manage_delObjects(ids)

        # install all the items
        svr = silva_root.service_view_registry
        backup = context.backup
        self.place_files(context.importfolder, svr, backup)

        # run the register-script
        silva_root.service_view_registry.register_silva_news()

        # and place the icons
        icons = context.icons.manage_copyObjects(context.icons.objectIds())
        silva_root.globals.manage_pasteObjects(icons)

    def place_files(self, fro, to, backup):
        """Helper function to setup the ZMI-stuff"""
        if not 'Manager' in fro.REQUEST.AUTHENTICATED_USER.getRoles():
            raise 'Unauthorized', 'You are not allowed to install Silva News'

        for item in fro.objectValues():
            if item.meta_type == 'Folder':
                # create the folder and recurse
                if not item.id in to.objectIds('Folder'):
                    to.manage_addFolder(item.id, item.title)
                newfolder = getattr(to, item.id)
                # copy properties (if any)
                for prop in item.propertyIds():
                    if not newfolder.hasProperty(prop):
                        newfolder.manage_addProperty(prop, item.getProperty(prop), item.getPropertyType(prop))
                    else:
                        newfolder.manage_changeProperties({prop: item.getProperty(prop)})
                backup.manage_addFolder(item.id, item.title)
                newbackup = getattr(backup, item.id)
                self.place_files(item, newfolder, newbackup)
            else:
                # copy the item
                if item.id in to.objectIds():
                    b = to.manage_cutObjects([item.id])
                    backup.manage_pasteObjects(b)
                cp = fro.manage_copyObjects([item.id])
                to.manage_pasteObjects(cp)

    def setup_catalog(self, context, silva_root):
        """Sets the ZCatalog up"""
        if not 'Manager' in context.REQUEST.AUTHENTICATED_USER.getRoles():
            raise 'Unauthorized', 'You are not allowed to install Silva News'

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
        # (Should probably be ISO-8859-1, but the Splitter crashes Zope 2.5.1?)
        catalog.Indexes['fulltext'].manage_setPreferences('UnicodeVocabulary')

modsec = ModuleSecurityInfo('Products.SilvaNews.install')
modsec.declarePublic('NewsInstaller')
modsec.apply(globals())
