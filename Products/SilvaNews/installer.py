from os import path

from App.Common import package_home

from silva.core.services.catalog import RecordStyle
from silva.core.conf.installer import DefaultInstaller

from Products.SilvaNews.interfaces import ISilvaNewsExtension


class SilvaNewsInstaller(DefaultInstaller):
    """Installer for the Silva News Service
    """
    not_globally_addables = ['Silva Article', 'Silva Agenda Item']

    def install_custom(self, root):
        self.setup_catalog(root)
        self.configure_extra_metadata(root)

        if not hasattr(root.aq_explicit,'service_news'):
            factory = root.manage_addProduct['SilvaNews']
            factory.manage_addServiceNews('service_news')

    def uninstall_custom(self, root):
        self.unconfigure_extra_metadata(root)

    def configure_extra_metadata(self, root):
        sm = root.service_metadata
        collection = sm.getCollection()
        if 'snn-np-settings' in collection.objectIds():
            collection.manage_delObjects(['snn-np-settings'])
        xml_file = path.join(package_home(globals()), 'snn-np-settings.xml')
        fh = open(xml_file, 'r')
        collection.importSet(fh)
        sm.addTypeMapping('Silva News Publication', ['snn-np-settings'])
        sm.initializeMetadata()

    def unconfigure_extra_metadata(self, root):
        sm = root.service_metadata
        collection = sm.getCollection()
        if 'snn-np-settings' in collection.objectIds():
            collection.manage_delObjects(['snn-np-settings'])
        sm.removeTypeMapping('Silva News Publication',['snn-np-settings'])

    def setup_catalog(self, root):
        """Sets the ZCatalog up"""
        catalog = root.service_catalog

        indexes = [
            ('parent_path', 'FieldIndex'),
            ('start_datetime', 'DateIndex'),
            ('end_datetime', 'DateIndex'),
            ('display_datetime', 'DateIndex'),
            ('timestamp_ranges', 'IntegerRangesIndex'),
            ('subjects', 'KeywordIndex'),
            ('target_audiences', 'KeywordIndex'),
            ]

        columns = ['display_datetime', 'start_datetime']

        existing_columns = catalog.schema()
        existing_indexes = catalog.indexes()

        for column in columns:
            if column not in existing_columns:
                catalog.addColumn(column)

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

install = SilvaNewsInstaller("SilvaNews", ISilvaNewsExtension)
