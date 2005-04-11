import unittest
try:
    from Products.SilvaNews.Tree import *
except ImportError:
    # allows running this test stand-alone, add the Products dir to
    # your PYTHONPATH
    from Tree import *

class TreeTestCase(unittest.TestCase):
    
    def setUp(self):
        self.root = Root()
        
        self.foo = foo = Node('foo', 'Foo')
        self.root.addChild(foo)

        self.bar = bar = Node('bar', 'Bar')
        self.root.addChild(bar)

        self.baz = baz = Node('baz', 'Baz')
        self.bar.addChild(baz)

    def test_addChild(self):
        self.assertEquals(len(self.root.children()), 2)

        qux = Node('qux', 'Qux')
        self.root.addChild(qux)

        self.assertEquals(len(self.root.children()), 3)

        self.assertEquals(len(self.foo.children()), 0)

        quux = Node('quux', 'Quux')
        self.foo.addChild(quux)
        self.assertEquals(len(self.foo.children()), 1)

        self.assertEquals(self.foo.children()[0].id(), 'quux')
        self.assertEquals(self.foo.children()[0].title(), 'Quux')

        newfoo = Node('foo', 'Foo')
        self.assertRaises(DuplicateIdError, self.root.addChild, newfoo)

    def test_getElement(self):
        self.assertEquals(self.root.getElement('root'), self.root)
        self.assertEquals(self.root.getElement('foo'), self.foo)
        self.assertEquals(self.root.getElement('bar'), self.bar)
        self.assertEquals(self.root.getElement('baz'), self.baz)

    def test_getIds(self):
        ids = self.root.getIds()
        ids.sort()
        self.assertEquals(ids, ['bar', 'baz', 'foo', 'root'])

    def test_removeChildren(self):
        self.assertRaises(ValueError, self.root.removeChild, self.baz)
        
        self.assertEquals(len(self.root.children()), 2)
        self.assert_('foo' in self.root.getIds())
        self.root.removeChild(self.foo)
        self.assertEquals(len(self.root.children()), 1)
        self.assert_('foo' not in self.root.getIds())

        self.assertEquals(len(self.root.children()), 1)
        self.assert_('bar' in self.root.getIds())
        self.root.removeChild(self.bar)
        self.assertEquals(len(self.root.children()), 0)
        self.assert_('bar' not in self.root.getIds())
        self.assert_('baz' not in self.root.getIds())

    def test_getElements(self):
        elids = [x.id() for x in self.root.getElements()]
        self.assertEquals(['foo', 'bar', 'baz'], elids)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TreeTestCase))
    return suite
    
if __name__ == '__main__':
    unittest.main()
