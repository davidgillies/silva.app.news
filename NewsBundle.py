# Python
from StringIO import StringIO
# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from OFS.Folder import Folder
from DateTime import DateTime
# Silva
from Products.Silva.IContent import IContent
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit

class XMLExportContext:
    pass

class NewsBundle(Content, Folder):
    """Export of a couple of agendaitems for creating a NewsBundle
    """

    security = ClassSecurityInfo()
    meta_type = 'Silva News NewsBundle'
    __implements__ = IContent

    def __init__(self, id, title):
        NewsBundle.inheritedAttribute('__init__')(self, id, title)
        self._articles = []
        self._main_article = None
        self._filters = []
        self._number_of_days = 31
        self._offset_days = 0
        self._statements = ""

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object_title')
    def object_title(self):
        """Returns the title
        """
        return self._title

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_visible')
    def is_visible(self):
        """Returns 0, because the viewers should NOT be shown in the TOC's
        """
        return 0

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_article')
    def set_article(self, articlepath, on_or_off):
        """Adds or removes an article from the bundle
        """
        if on_or_off and articlepath not in self._articles:
            self._articles.append(articlepath)
        elif not on_or_off and articlepath in self._articles:
            self._articles.remove(articlepath)
        self._p_changed = 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'articles')
    def articles(self):
        """Returns all articles
        """
        self._verify_articles()
        return self._articles

    def article_titles(self):
        out = []
        for a in self.articles():
            obj = self.restrictedTraverse(a)
            out.append(('%s (%s)' % (obj.get_title_html(), a), a))
        return out

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'filters')
    def main_article(self):
        return self._main_article

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_main_article')
    def set_main_article(self, articlepath):
        """Sets the main article
        """
        self._main_article = articlepath
        self._p_changed = 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_filter')
    def set_filter(self, filterpath, on_or_off):
        """Adds or removes a filter from the filterlist
        """
        if on_or_off and filterpath not in self._filters:
            self._filters.append(filterpath)
        elif not on_or_off and filterpath in self._filters:
            self._filters.remove(filterpath)
        self._p_changed = 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'filters')
    def filters(self):
        """Returns the filterlist
        """
        return self._filters

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'findfilters')
    def findfilters(self):
        """Finds all available filters for this bundle
        """
        query = {'meta_type': 'Silva News AgendaFilter'}
        results = self.service_catalog(query)

        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'findfilters_pairs')
    def findfilters_pairs(self):
        """Returns the filters as pairs (title, path) for rendering in a Formulator form
        """
        return [(f.get_title_html, f.getPath()) for f in self.findfilters()]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_all_articles')
    def get_all_articles(self):
        """Returns all the items in the filters
        """
        if not self._filters:
            return []
        print "Getting articles from filters %s" % self._filters
        now = DateTime()
        lastnight = DateTime(now.year(), now.month(), now.day(), 0, 0, 0)
        offset = lastnight + self._offset_days
        for f in self._filters:
            obj = self.restrictedTraverse(f)
            print "Getting next items from object %s" % obj
            res = obj.get_next_items(self._number_of_days + self._offset_days)
            final = []
            for item in res:
                if item.start_datetime >= offset:
                    final.append(item)
        final = self._delete_doubles(final)
        return final

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_xml')
    def get_xml(self):
        """Creates an XML-document for the bundle
        """
        self._verify_articles()
        context = XMLExportContext()
        context.f = StringIO()
        context.f.write(u'<?xml version="1.0" ?>\n<newsbundle>\n')
        context.f.write(u'<title>%s</title>\n' % self.object_title())
        context.f.write(u'<statements>%s</statements>\n' % self._prepare_xml(self._statements))
        # write the main article first...
        main_article = self.restrictedTraverse(self._main_article)
        context.f.write(u'<main_article type="%s">\n' % main_article.meta_type)
        main_article.to_xml(context)
        context.f.write(u'</main_article>\n')
        # Each of the articles in self._articles should be printed in full
        for item in self._articles:
            if item != self._main_article:
                obj = self.restrictedTraverse(item)
                context.f.write(u'<article type="%s">\n' % obj.meta_type)
                obj.to_xml(context)
                context.f.write(u'</article>\n')
        # A part of each article in the filter should be in the agenda
        context.f.write(u'<agenda>\n')
        for item in [f.getPath() for f in self.get_all_articles()]:
            obj = self.restrictedTraverse(item)
            context.f.write(u'<summary type="%s">\n' % obj.meta_type)
            obj.to_summary_xml(context)
            context.f.write(u'</summary>\n')
        context.f.write(u'</agenda>\n')
        context.f.write(u'</newsbundle>\n')
        xml = context.f.getvalue()
        return xml.encode('UTF-8')

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'statements')
    def statements(self):
        """Returns the statements (plain string)
        """
        return self._statements

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'set_statements')
    def set_statements(self, statements):
        """Sets the statements-string
        """
        self._statements = statements
        self._p_changed = 1

    def _delete_doubles(self, res):
        out = []
        found = []
        for item in res:
            path = item.getPath()
            if not path in found:
                out.append(item)
                found.append(path)
        return out

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'number_of_days')
    def number_of_days(self):
        """Returns number_of_days
        """
        return self._number_of_days

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_number_of_days')
    def set_number_of_days(self, number):
        """Sets number of days
        """
        self._number_of_days = number
        self._p_changed = 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'offset_days')
    def offset_days(self):
        """Returns offset_days
        """
        return self._offset_days

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_offset_days')
    def set_offset_days(self, number):
        """Sets offset in days
        """
        self._offset_days = number
        self._p_changed = 1

    def _verify_articles(self):
        allowed_article_paths = [f.getPath() for f in self.get_all_articles()]
        for article in self._articles:
            if not article in allowed_article_paths:
                self._articles.remove(article)

    def _prepare_xml(self, plaintext):
        xml = unicode(plaintext, 'cp1252')
        xml = xml.replace('&', '&amp;')
        xml = xml.replace('<', '&lt;')
        xml = xml.replace('>', '&gt;')

        return xml

InitializeClass(NewsBundle)

manage_addNewsBundleForm = PageTemplateFile("www/newsBundleAdd", globals(),
                                             __name__='manage_addNewsBundleForm')

def manage_addNewsBundle(self, id, title, create_default=1, REQUEST=None):
    """Add a Silva NewsBundle."""
    if not self.is_id_valid(id):
        return
    object = NewsBundle(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
