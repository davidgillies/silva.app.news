
import unittest
from datetime import datetime

from Products.Silva.testing import TestRequest, tests
from Products.SilvaMetadata.interfaces import IMetadataService
from zope.component import getUtility
from zope.interface.verify import verifyObject

from silva.app.news.AgendaItem.content import AgendaItemOccurrence
from silva.app.news.codesources.inline import get_items
from silva.app.news.interfaces import INewsItemReference
from silva.app.news.testing import FunctionalLayer
from silva.core.interfaces import IPublicationWorkflow
from silva.core.references.reference import get_content_id


class InlineNewsViewerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        # Test image
        factory = self.root.manage_addProduct['Silva']
        with self.layer.open_fixture('content-listing.png', globals()) as image:
            factory.manage_addImage('listing', 'Listing', image)
        # Test news contents
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News')
        factory = self.root.news.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('release', 'Relase of a code source')
        factory.manage_addNewsItem('testing', 'Testing of a code source')
        factory.manage_addAgendaItem('debugging', 'Debugging of a code source')
        self.root.news.filter.set_show_agenda_items(True)

        timezone = self.root.news.index.default_timezone()
        version = self.root.news.debugging.get_editable()
        version.set_occurrences([AgendaItemOccurrence(
                    start_datetime=datetime(2012, 07, 10, 8, 0, tzinfo=timezone),
                    end_datetime=datetime(2012, 07, 15, 18, 0, tzinfo=timezone),
                    location=u'Rotterdam')])

    def test_news_item_no_text_news_item_reference(self):
        """Test the NewsitemReference for a NewsItem
        """
        # Publish news item so we see it.
        IPublicationWorkflow(self.root.news.testing).publish()
        version = self.root.news.testing.get_viewable()

        items = get_items(self.root.news.index, TestRequest(), 10)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertTrue(verifyObject(INewsItemReference, item))
        self.assertEqual(item.context, version)
        self.assertEqual(item.id(), 'testing')
        self.assertEqual(item.title(), 'Testing of a code source')
        self.assertEqual(item.description(), '')
        self.assertEqual(item.thumbnail(), '')
        # XXX Later empty introduction should return an empty string.
        self.assertEqual(item.introduction(), '<p></p>')
        self.assertEqual(item.link(), 'http://localhost/root/news/testing')
        self.assertEqual(item.creation_datetime(), version.get_display_datetime())
        self.assertEqual(item.start_datetime(), None)
        self.assertEqual(item.end_datetime(), None)
        self.assertEqual(item.location(), None)

    def test_news_item_with_text_news_item_reference(self):
        """Test the NewsitemReference for a NewsItem
        """
        version = self.root.news.testing.get_editable()
        version.body.save(
            version,
            TestRequest(),
            u"""<h2>Today is the day of the Internet!</h2>
<h3>Yes it is</h3>
<p>
  This the day of free internet ! The Internet is a global system of
  interconnected computer networks that use the standard Internet
  protocol suite (often called TCP/IP, although not all applications
  use TCP) to serve billions of users worldwide. It is a network of
  networks that consists of millions of private, public, academic,
  business, and government networks, of local to global scope, that
  are linked by a broad array of electronic, wireless and optical
  networking technologies. The Internet carries an extensive range of
  information resources and services, such as the inter-linked
  hypertext documents of the World Wide Web (WWW) and the
  infrastructure to support email.
</p>
<div class="image">
  <img src="foo" data-silva-reference="news" data-silva-target="%s" />
</div>
<p>
  I am not kidding.
</p>
""" % (get_content_id(self.root.listing)))
        binding = getUtility(IMetadataService).getMetadata(version)
        binding.setValues(
            'silva-extra',
            {'content_description':
                 'This is an exciting news item about the Interwebs.'})
                               

        # Publish news item so we see it.
        IPublicationWorkflow(self.root.news.testing).publish()
        version = self.root.news.testing.get_viewable()

        items = get_items(self.root.news.index, TestRequest(), 10)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertTrue(verifyObject(INewsItemReference, item))
        self.assertEqual(item.context, version)
        self.assertEqual(item.id(), 'testing')
        self.assertEqual(
            item.title(),
            'Testing of a code source')
        self.assertEqual(
            item.description(),
            'This is an exciting news item about the Interwebs.')
        self.assertEqual(
            item.description(10),
            'This is an')
        tests.assertXMLEqual(
            item.thumbnail(),
            u"""<div class="inv_thumbnail">
   <a class="newsitemthumbnaillink" href="http://localhost/root/news/testing">
      <img src="http://localhost/root/listing?thumbnail" class="thumbnail" />
   </a>
</div>""")
        tests.assertXMLEqual(
            item.introduction(),
            u"""
<p> 
  This the day of free internet ! The Internet is a global system of
  interconnected computer networks that use the standard Internet
  protocol suite (often called TCP/IP, although not all applications
  use TCP) to serve billions of users worldwide. It is a network of
  networks that consists of millions of private, public, academic,
  business, and government networks, of local to global scope, that
  are linked by a broad array of electronic, wireless and optical
  networking technologies. The Internet carries an extensive range of
  information resources and services, such as the inter-linked
  hypertext documents of the World Wide Web (WWW) and the
  infrastructure to support email.
</p>""")
        tests.assertXMLEqual(
            item.introduction(128),
            u"""
<p> 
  This the day of free internet ! The Internet is a global system of interconnected computer networks that use the standard Inter&#8230;
</p>""")
        self.assertEqual(item.link(), 'http://localhost/root/news/testing')
        self.assertEqual(item.start_datetime(), None)
        self.assertEqual(item.end_datetime(), None)
        self.assertEqual(item.location(), None)

    def test_agenda_item_news_item_reference(self):
        """Test specific implementation of NewsItemReference for
        AgendaItem.
        """
        IPublicationWorkflow(self.root.news.debugging).publish()
        version = self.root.news.debugging.get_viewable()
        timezone = self.root.news.index.default_timezone()

        items = get_items(self.root.news.index, TestRequest(), 10)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertTrue(verifyObject(INewsItemReference, item))
        self.assertEqual(item.context, version)
        self.assertEqual(item.id(), 'debugging')
        self.assertEqual(item.title(), 'Debugging of a code source')
        self.assertEqual(
            item.start_datetime(),
            datetime(2012, 7, 10, 8, 0, tzinfo=timezone))
        self.assertEqual(
            item.end_datetime(),
            datetime(2012, 07, 15, 18, 0, 0, tzinfo=timezone))
        self.assertEqual(
            item.location(), u'Rotterdam')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InlineNewsViewerTestCase))
    return suite
