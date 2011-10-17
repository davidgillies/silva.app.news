# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.app.news.tests.SilvaNewsTestCase import SilvaNewsTestCase
from Products.Silva.roleinfo import AUTHOR_ROLES


class SilvaNewsInstallerTestCase(SilvaNewsTestCase):

    def test_installation(self):
        self.assertEqual(
            self.root.service_extensions.is_installed('silva.app.news'),
            True)

    def test_catalog_indexes(self):
        #ensure catalog indexes are setup
        catalog = self.catalog
        indexes = [
            ('parent_path', 'FieldIndex'),
            ('sort_index', 'FieldIndex'),
            ('display_datetime', 'DateIndex'),
            ('subjects', 'KeywordIndex'),
            ('target_audiences', 'KeywordIndex'),
        ]
        existing_indexes = catalog.getIndexObjects()
        for (id,mt) in indexes:
            index = None
            for i in existing_indexes:
                if i.id == id:
                    index = i
                    break
            self.assertEqual(id, index.id)
            self.assertEqual(index.meta_type,mt)

    def test_security(self):
        #ensure addable security is assigned to the
        # appropriate roles
        root = self.root
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
        possible_permissions = root.possible_permissions()
        a_roles = list(AUTHOR_ROLES[:])
        a_roles.sort()
        for perm in add_permissions:
            if perm in possible_permissions:
                roles = [ r['name'] for r in root.rolesOfPermission(perm)
                          if r['selected'] == 'SELECTED' ]
                self.assertEqual(a_roles,roles)

    def test_addables(self):
        # make sure the root addables doesn't include
        # news/agenda items
        addables = self.root.get_silva_addables_allowed_in_container()
        allowed_snn_types = ['Silva Agenda Filter','Silva Agenda Viewer',
                             'Silva News Category Filter',
                             'Silva News Filter', 'Silva News Publication',
                             'Silva News Viewer', 'Silva RSS Aggregator']
        for allowed in allowed_snn_types:
            self.assert_(allowed in addables)
        disallowed_snn_types = ['Silva Article', 'Silva Agenda Item']
        for dis in disallowed_snn_types:
            self.assert_(dis not in addables)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaNewsInstallerTestCase))
    return suite
