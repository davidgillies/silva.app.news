# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
"""Simple generic tree implementation
"""
from zope.interface import Interface, implements


class IReadableNode(Interface):
    """Node of a tree.
    """

    def id():
        """Return node id.
        """

    def title():
        """Return node title.
        """

    def parent():
        """Return the parent.
        """

    def children():
        """Return the direct childrens.
        """

    def get_ids(depth=-1):
        """Return all ids of child nodes.
        """


class IReadableRoot(IReadableNode):
    """Root of a tree.
    """

    def get_element(id):
        """Return a node by its id.
        """

    def get_elements():
        """Return all nodes.
        """

class IWritableNode(IReadableNode):

    def set_id(id):
        """Change node id.
        """

    def set_title(title):
        """Change node title.
        """

    def add_child(child):
        """Add a new child to this node.
        """

    def remove_child(child):
        """Remove a child from this node.
        """

class IWritableRoot(IReadableRoot, IWritableNode):
    pass


class DuplicateIdError(ValueError):
    """Raised when an id is already in use
    """


class Node:
    """A single tree node
    """
    # XXX it would be great to use a new-style class, but there are pickles
    implements(IWritableNode)

    def __init__(self, id, title):
        self._id = id
        self._title = title
        self._children = []
        self._parent = None
        self._root = None

    def id(self):
        return self._id

    def title(self):
        return self._title

    def children(self):
        return self._children

    def parent(self):
        return self._parent

    def set_id(self, id):
        if id in self._root.get_ids():
            raise DuplicateIdError(
                u'identifier already in use - %s' % id)
        del self._root._references[self._id]
        self._id = id
        self._root._references[id] = self

    def set_title(self, title):
        self._title = title

    def add_child(self, child):
        if child.id() in self._root.get_ids():
            raise DuplicateIdError(
                u'identifier already in use  - %s' % child.id())
        self._children.append(child)
        child._parent = self
        child._set_root(self._root)

    def remove_child(self, child):
        for c in child.children():
            child.remove_child(c)
        del self._children[self._children.index(child)]
        self._root._del_element(child)
        del child._parent
        del child._root

    def _set_root(self, root):
        self._root = root
        self._root._references[self._id] = self

    def get_ids(self, depth=-1):
        results = [self._id]
        if depth:
            for node in self._children:
                results.extend(node.get_ids(max(depth - 1, -1)))
        return results


class Root(Node):
    implements(IWritableRoot)

    def __init__(self):
        Node.__init__(self, 'root', 'root')
        self._references = {'root': self}
        self._root = self

    def get_element(self, id):
        """returns an element by id"""
        return self._references[id]

    def get_elements(self):
        return self._references.values()

    def get_ids(self, depth=-1):
        """returns list of all used ids"""
        if depth != -1:
            return Node.get_ids(self, depth=depth)
        return self._references.keys()

    def _del_element(self, child):
        del self._references[child.id()]


class FilteredNode(object):
    """Filter a node only allowing some of the children nodes.
    """
    implements(IReadableNode)

    def __init__(self, node, allowed):
        self._node = node
        self._allowed = allowed

    def id(self):
        return self._node.id()

    def title(self):
        return self._node.title()

    def parent(self):
        node = self._node.parent()
        if node is not None:
            return FilteredNode(node, self._allowed)
        return None

    def children(self):
        result = []
        for node in self._node.children():
            if node.id() in self._allowed:
                result.append(FilteredNode(node, self._allowed))
        return result

    def get_ids(self, depth=-1):
        return list(self._allowed.intersection(self._node.get_ids(depth=depth)))


class FilteredTree(FilteredNode):
    """Filter a tree only allowing some of the children nodes.
    """
    implements(IReadableRoot)

    def get_element(self, id):
        if id in self._allowed:
            node = self._node.get_element(id)
            if node is not None:
                return FilteredNode(node, self._allowed)
        return None

    def get_elements(self):
        result = []
        for id in self.get_ids():
            node = self._node.get_element(id)
            if node is not None:
                result.append(FilteredNode(node, self._allowed))
        return result


def create_filtered_tree(tree, allowed):
    """Create a filtered tree. Add all missing parent ids to allowed.
    """
    ids = set()
    for id in allowed:
        node = tree.get_element(id)
        if node is not None:
            # Add self and all the children
            ids.update(node.get_ids())
            # Add all the parent
            node = node.parent()
            while node is not None:
                if node.id() in ids:
                    break
                ids.add(node.id())
                node = node.parent()
    return FilteredTree(tree, ids)
