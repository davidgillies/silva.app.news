from DateTime import DateTime

from silva.app.news.tests.SilvaNewsTestCase import SilvaNewsTestCase

class TestRendering(SilvaNewsTestCase):

    host = "http://localhost/"

    def setUp(self):
        super(TestRendering, self).setUp()
        self.browser = self.layer.get_browser()
        self.browser.options.handle_errors = False

    def test_render_simple_article(self):
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsItem('article', 'Article from SilvaNews')
        article = self.root.article
        article.set_unapproved_version_publication_datetime(DateTime())
        article.approve_version()
        status = self.browser.open(self.get_url(article))
        self.assertEquals(status, 200)
        self.assertTrue('Article from SilvaNews' in self.browser.contents)

    def get_url(self, obj):
        return self.host + "/".join(obj.getPhysicalPath())
