# set the software version, NOTE THAT THIS MUST BE UP-TO-DATE for
# the upgrade to work correctly!!
# use only major and minor version parts, upgrade shouldn't happen
# on patch-level updates
software_version = '2.8'

from installer import install

from silva.core import conf as silvaconf

silvaconf.extensionName("SilvaNews")
silvaconf.extensionTitle("Silva News Network")
silvaconf.extensionDepends(["SilvaDocument","SilvaExternalSources"])

def initialize(context):
    from Products.SilvaNews.silvaxml import xmlexport, xmlimport
    xmlexport.initializeXMLExportRegistry()
    xmlimport.initializeXMLImportRegistry()

import dates
def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('dates',)

# import the actual upgraders
import upgrade_13, upgrade_20, upgrade_21
