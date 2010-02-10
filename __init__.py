from installer import install

from silva.core import conf as silvaconf

silvaconf.extensionName("SilvaNews")
silvaconf.extensionTitle("Silva News Network")
silvaconf.extensionDepends(["SilvaDocument","SilvaExternalSources"])

def initialize(context):
    from Products.SilvaNews.silvaxml import xmlexport, xmlimport
    xmlexport.initializeXMLExportRegistry()
    xmlimport.initializeXMLImportRegistry()
    
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

# import the actual upgraders
import upgrade_13, upgrade_20, upgrade_21, upgrade_28
