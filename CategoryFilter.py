from zope.interface import implements

# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

# Silva/News Interfaces
from interfaces import ICategoryFilter

# Silva/News
from Products.Silva import SilvaPermissions
from Products.Silva.i18n import translate as _
from Products.SilvaNews.Filter import Filter
from Products.SilvaNews.ServiceNews import CategoryMixin

class CategoryFilter(Filter,CategoryMixin):
    """A Category Filter is useful in large sites where the news articles have
       (too) many subjects and target audiences defined. The Filter will limit
       those that display so only the appropriate ones for that area of the
       site appear.
    """

    security = ClassSecurityInfo()

    meta_type = "Silva News Category Filter"

    implements(ICategoryFilter)

    def __init__(self, id):
        Filter.__init__(self, id)

InitializeClass(CategoryFilter)
