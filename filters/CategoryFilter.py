from zope.interface import implements

# Zope
from App.class_init import InitializeClass # Zope 2.12

from AccessControl import ClassSecurityInfo

# Silva
from silva.core import conf as silvaconf

# SilvaNews
from Products.SilvaNews.interfaces import ICategoryFilter
from Products.SilvaNews.filters.Filter import Filter
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
    silvaconf.icon("www/category_filter.png")
    silvaconf.priority(3.6)

    def __init__(self, id):
        Filter.__init__(self, id)

InitializeClass(CategoryFilter)
