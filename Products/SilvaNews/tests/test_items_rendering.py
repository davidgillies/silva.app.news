import unittest
from DateTime import DateTime

from Products.Silva.testing import Browser
from Products.SilvaNews.tests.SilvaNewsTestCase import SilvaNewsTestCase

class TestRendering(SilvaNewsTestCase):

    host = "http://localhost/"

    def setUp(self):
        super(TestRendering, self).setUp()
        self.browser = Browser()
        self.browser.handleErrors = False
        self.browser.raiseHttpErrors = True

    def test_render_simple_article(self):
        factory = self.root.manage_addProduct['SilvaNews']
        factory.manage_addPlainArticle('article', 'Article from SilvaNews')
        article = self.root.article
        version = getattr(self.root.article, '0')
        article.set_unapproved_version_publication_datetime(DateTime())
        article.approve_version()
        self.browser.open(self.get_url(article))
        self.assertEquals(self.browser.status, '200 OK')
        self.assertTrue('Article from SilvaNews' in self.browser.contents)

    def get_url(self, obj):
        return self.host + "/".join(obj.getPhysicalPath())
