# Zope
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
# Silva
from Products.Silva.EditorSupport import EditorSupport
from Products.Silva import SilvaPermissions
from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.IVersionedContent import IVersionedContent
from Products.Silva.helpers import add_and_edit
from Products.ParsedXML.ParsedXML import ParsedXML
from NewsItem import NewsItem, NewsItemVersion
from Interfaces import INewsItem

class Article(NewsItem):
    """Silva News Article.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News Article"

    __implements__ = INewsItem, IVersionedContent

    # MANIPULATORS

    # ACCESSORS

InitializeClass(Article)

class ArticleVersion(NewsItemVersion):
    """Silva News Article version.
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News Article Version"

    def __init__(self, id):
        ArticleVersion.inheritedAttribute('__init__')(self, id)
        self._subheader = ''
        self._lead = ''
        self._pressnote = ''
        self.content = ParsedXML('content', '<doc></doc>')

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_article_data')
    def set_article_data(self, subheader, lead, pressnote,
                         common_info, specific_info, manual_specific_info,
                         subjects, target_audiences, embargo_datetime, more_info_links):
        self._subheader = subheader
        self._lead = lead
        self._pressnote = pressnote
        self._common_info = common_info
        self._specific_info = specific_info
        self._manual_specific_info = manual_specific_info
        self._subjects = subjects
        self._target_audiences = target_audiences
        self._embargo_datetime = embargo_datetime
        self._more_info_links = [item.split('|') for item in more_info_links.split('\n') if item] # Filters out empty lines
        # FIXME: It would be nice if this could be moved upwards in the class-hierarchy
        # reindex is acquired from the object
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_article_data_without_subjects_target_audiences')
    def set_article_data_without_subjects_target_audiences(self, subheader, lead, pressnote,
                         common_info, specific_info, manual_specific_info,
                         embargo_datetime, more_info_links):
        self._subheader = subheader
        self._lead = lead
        self._pressnote = pressnote
        self._common_info = common_info
        self._specific_info = specific_info
        self._manual_specific_info = manual_specific_info
        self._embargo_datetime = embargo_datetime
        self._more_info_links = [item.split('|') for item in more_info_links.split('\n') if item] # Filters out empty lines
        # FIXME: It would be nice if this could be moved upwards in the class-hierarchy
        # reindex is acquired from the object
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_article_data_subjects_target_audiences')
    def set_article_data_subjects_target_audiences(self, subjects, target_audiences):
        self._subjects = subjects
        self._target_audiences = target_audiences
        # FIXME: It would be nice if this could be moved upwards in the class-hierarchy
        # reindex is acquired from the object
        self.reindex_object()

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'subheader')
    def subheader(self):
        """Returns subheader
        """
        return self._subheader

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'lead')
    def lead(self):
        """Returns the lead
        """
        return self._lead

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'pressnote')
    def pressnote(self):
        """Returns pressnote
        """
        return self._pressnote

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Deliver the contents as plain text, for full-text search
        """
        parenttext = ArticleVersion.inheritedAttribute('fulltext')(self)
        content = self._flattenxml(str(self.content))
        return "%s %s %s %s" % (parenttext, self._subheader, self._pressnote,
                                      content)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_xml')
    def to_xml(self, context):
        """Returns the contents of this object as a partial XML-doc
        """
        ArticleVersion.inheritedAttribute('to_xml')(self, context)
        xml = u'<subheader>%s</subheader>\n' % self._prepare_xml(self._subheader)
        xml += u'<lead>%s</lead>\n' % self._prepare_xml(self._lead)
        xml += u'<pressnote>%s</pressnote>\n' % self._prepare_xml(self._pressnote)
        xml += u'<content>\n%s\n</content>\n' % self.content_xml()

        context.f.write(xml)

InitializeClass(ArticleVersion)

manage_addArticleForm = PageTemplateFile(
    "www/articleAdd", globals(),
    __name__='manage_addArticleForm')

def manage_addArticle(self, id, title, REQUEST=None):
    """Add a News Article."""
    if not self.is_id_valid(id):
        return
    object = Article(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object._setObject('0', ArticleVersion('0'))
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addArticleVersionForm = PageTemplateFile(
    "www/articleVersionAdd",
    globals() ,
    __name__='manage_addArticleVersionForm')

def manage_addArticleVersion(self, id, REQUEST=None):
    """Add a Article version."""
    object = ArticleVersion(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''
