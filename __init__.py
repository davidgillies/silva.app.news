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


