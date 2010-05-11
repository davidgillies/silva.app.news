from silva.core.upgrade.upgrade import BaseUpgrader

VERSION = '2.3a1'

class DocumentUpgrader(BaseUpgrader):

    def upgrade(self, obj):
        parsed_xml = obj.content._content
        obj.content = parsed_xml
        return obj

document_upgrader_agenda = \
    DocumentUpgrader(VERSION, 'Silva Agenda Item Version', 100)
document_upgrader_article = \
    DocumentUpgrader(VERSION, 'Silva Article Version', 100)
