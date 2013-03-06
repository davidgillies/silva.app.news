# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from os import path

from App.Common import package_home

from silva.core.editor.interfaces import ICKEditorService
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface
from zope.component import getUtility, queryUtility


class IExtension(Interface):
    """silva.app.news extension
    """


class SilvaNewsInstaller(DefaultInstaller):
    """Installer for the Silva News Service
    """
    not_globally_addables = ['Silva News Item', 'Silva Agenda Item']

    def install_custom(self, root):
        self.setup_catalog(root)
        self.configure_extra_metadata(root)

        if queryUtility(ICKEditorService) is None:
            factory = root.manage_addProduct['silva.core.editor']
            factory.manage_addCKEditorService()

        declare = getUtility(ICKEditorService).declare_configuration
        declare('Silva News Item', ['Silva Document'])
        declare('Silva Agenda Item', ['Silva News Item', 'Silva Document'])

        if 'service_news' not in root.objectIds():
            factory = root.manage_addProduct['silva.app.news']
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
            ('sort_index', 'FieldIndex'),
            ('parent_path', 'FieldIndex'),
            ('display_datetime', 'DateIndex'),
            ('timestamp_ranges', 'IntegerRangesIndex'),
            ('subjects', 'KeywordIndex'),
            ('target_audiences', 'KeywordIndex'),
            ]

        columns = ['display_datetime', 'sort_index']

        existing_columns = catalog.schema()
        existing_indexes = catalog.indexes()

        for column in columns:
            if column not in existing_columns:
                catalog.addColumn(column)

        for field_name, field_type in indexes:
            if field_name not in existing_indexes:
                catalog.addIndex(field_name, field_type)


install = SilvaNewsInstaller("silva.app.news", IExtension)
