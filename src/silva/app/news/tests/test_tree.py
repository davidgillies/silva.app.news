# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from silva.app.news.Tree import Root, Node, create_filtered_tree
from silva.app.news.Tree import DuplicateIdError
from silva.app.news.Tree import IWritableRoot, IWritableNode
from silva.app.news.Tree import IReadableRoot, IReadableNode
from zope.interface.verify import verifyObject


class TreeTestCase(unittest.TestCase):

    def setUp(self):
        self.root = Root()

        self.child1 = child1 = Node('child1', 'Child1')
        self.root.add_child(child1)

        self.child2 = child2 = Node('child2', 'Child2')
        self.root.add_child(child2)

        self.grand1child2 = grand1child2 = Node('grand1child2', 'Grand1child2')
        self.child2.add_child(grand1child2)

    def test_node(self):
        child1 = self.root.get_element('child1')
        self.assertTrue(verifyObject(IWritableNode, child1))
        self.assertEqual(child1.id(), 'child1')
        self.assertEqual(child1.title(), 'Child1')
        self.assertEqual(child1.parent(), self.root)

        child1.set_id('new child1')
        self.assertEqual(child1.id(), 'new child1')

        # Cannot rename to a used id
        with self.assertRaises(DuplicateIdError):
            child1.set_id('child2')
        self.assertEqual(child1.id(), 'new child1')

        child1.set_title('New Child1')
        self.assertEqual(child1.title(), 'New Child1')

    def test_add_child(self):
        self.assertEquals(len(self.root.children()), 2)

        self.root.add_child(Node('qux', 'Qux'))
        self.assertEquals(len(self.root.children()), 3)
        self.assertEquals(len(self.child1.children()), 0)

        self.child1.add_child(Node('quux', 'Quux'))
        self.assertEquals(len(self.child1.children()), 1)

        self.assertEquals(self.child1.children()[0].id(), 'quux')
        self.assertEquals(self.child1.children()[0].title(), 'Quux')

        with self.assertRaises(DuplicateIdError):
            self.root.add_child(Node('child1', 'Duplicate Child1'))

    def test_get_ids(self):
        self.assertItemsEqual(
            self.root.get_ids(),
            ['child2', 'grand1child2', 'child1', 'root'])
        self.assertItemsEqual(
            self.root.get_ids(depth=1),
            ['child2', 'child1', 'root'])

    def test_remove_children(self):
        self.assertRaises(ValueError, self.root.remove_child, self.grand1child2)

        self.assertEquals(len(self.root.children()), 2)
        self.assertTrue('child1' in self.root.get_ids())
        self.root.remove_child(self.child1)
        self.assertEquals(len(self.root.children()), 1)
        self.assertTrue('child1' not in self.root.get_ids())

        self.assertEquals(len(self.root.children()), 1)
        self.assertTrue('child2' in self.root.get_ids())
        self.root.remove_child(self.child2)
        self.assertEquals(len(self.root.children()), 0)
        self.assertTrue('child2' not in self.root.get_ids())
        self.assertTrue('grand1child2' not in self.root.get_ids())

    def test_root(self):
        self.assertTrue(verifyObject(IWritableNode, self.root))
        self.assertTrue(verifyObject(IWritableRoot, self.root))

        self.assertEquals(self.root.get_element('root'), self.root)
        self.assertEquals(self.root.get_element('child1'), self.child1)
        self.assertEquals(self.root.get_element('child2'), self.child2)
        self.assertEquals(self.root.get_element('grand1child2'), self.grand1child2)

        self.assertItemsEqual(
            [x.id() for x in self.root.get_elements()],
            ['child1', 'child2', 'grand1child2', 'root'])

    def test_filtered_root(self):
        filtered_root = create_filtered_tree(self.root, ['child1'])
        self.assertTrue(verifyObject(IReadableNode, filtered_root))
        self.assertTrue(verifyObject(IReadableRoot, filtered_root))

        self.assertItemsEqual(
            [x.id() for x in filtered_root.get_elements()],
            ['child1', 'root'])

        filtered_node = filtered_root.get_element('child1')
        self.assertTrue(verifyObject(IReadableNode, filtered_node))
        self.assertEqual(filtered_node.id(), 'child1')
        self.assertEqual(filtered_node.title(), 'Child1')
        self.assertEqual(filtered_node.parent().id(), 'root')

        filtered_node = filtered_root.get_element('child2')
        self.assertEqual(filtered_node, None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TreeTestCase))
    return suite

