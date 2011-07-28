
from Products.ParsedXML.ParsedXML import ParsedXML

from silva.core.upgrade.upgrade import BaseUpgrader
from silva.core.upgrade.upgrader.upgrade_230 import VersionedContentUpgrader
from Products.SilvaDocument.upgrader.upgrade_230 import DocumentUpgrader
import logging


logger = logging.getLogger('silva.core.upgrade')

#-----------------------------------------------------------------------------
# 2.2.0 to 2.3.0b1
#-----------------------------------------------------------------------------

VERSION_B1='2.3b1'


class ArticleUpgrader(BaseUpgrader):

    def upgrade(self, obj):
        for version in obj.objectValues():
            if not isinstance(version.content, ParsedXML):
                logger.info('upgrade xmlattribute for %s' %
                            "/".join(version.getPhysicalPath()))
                parsed_xml = version.content._content
                version.content = parsed_xml
        return obj



article_upgrader_agenda = ArticleUpgrader(
    VERSION_B1, ['Silva Agenda Item', 'Silva Article'])
article_cache_upgrader = VersionedContentUpgrader(
    VERSION_B1, ['Silva Article', 'Silva Agenda Item'])


document_upgrader_agenda = DocumentUpgrader(
    VERSION_B1, ["Silva Agenda Item Version", "Silva Article Version"], 1000)


