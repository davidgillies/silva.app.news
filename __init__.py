from installer import install

from silva.core import conf as silvaconf

silvaconf.extensionName("SilvaNews")
silvaconf.extensionTitle("Silva News Network")
silvaconf.extensionDepends(["SilvaDocument","SilvaExternalSources"])

from Products.SilvaNews.silvaxml import xmlexport, xmlimport
xmlexport.initializeXMLExportRegistry()
xmlimport.initializeXMLImportRegistry()


def initialize(context):
    from Products.SilvaNews import indexing
    context.registerClass(
        indexing.IntegerRangesIndex,
        permission = 'Add Pluggable Index',
        constructors = (indexing.manage_addIntegerRangesIndexForm,
                        indexing.manage_addIntegerRangesIndex),
        visibility=None
        )


import dates
def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('dates',)


CLASS_CHANGES = {
        'Products.SilvaNews.silvaxmlattribute SilvaXMLAttribute':
            'OFS.SimpleItem SimpleItem',

        # filters

        'Products.SilvaNews.AgendaFilter AgendaFilter':
            'Products.SilvaNews.filters.AgendaFilter AgendaFilter',
        'Products.SilvaNews.CategoryFilter CategoryFilter':
            'Products.SilvaNews.filters.CategoryFilter CategoryFilter',
        'Products.SilvaNews.Filter Filter':
            'Products.SilvaNews.filters.Filter Filter',
        'Products.SilvaNews.NewsFilter NewsFilter':
            'Products.SilvaNews.filters.NewsFilter NewsFilter',
        'Products.SilvaNews.NewsItemFilter NewsItemFilter':
            'Products.SilvaNews.filters.NewsItemFilter NewsItemFilter',

        # viewers

        'Products.SilvaNews.AgendaViewer AgendaViewer':
            'Products.SilvaNews.viewers.AgendaViewer AgendaViewer',
        'Products.SilvaNews.InlineViewer InlineViewer':
            'Products.SilvaNews.viewers.InlineViewer InlineViewer',
        'Products.SilvaNews.NewsViewer NewsViewer':
            'Products.SilvaNews.viewers.NewsViewer NewsViewer',
    }

