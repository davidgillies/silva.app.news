from five import grok
from zope.interface import Attribute, Interface
from zope.schema import TextLine
from zope.schema.interfaces import ITextLine
from zope.traversing.browser import absoluteURL

from zeam.form.base.markers import DISPLAY
from zeam.form.ztk.fields import (SchemaField, SchemaFieldWidget,
    registerSchemaField)


class IPath(ITextLine):
    html_target = Attribute('html target')


class Path(TextLine):
    grok.implements(IPath)

    def __init__(self, html_target=None, **kw):
        self.html_target = html_target
        super(Path, self).__init__(**kw)


class PathSchemaField(SchemaField):
    """ zeam schema field
    """
    @property
    def html_target(self):
        return self._field.html_target


class PathWidgetDisplay(SchemaFieldWidget):
    grok.adapts(PathSchemaField, Interface, Interface)
    grok.name(str(DISPLAY))

    def htmlTarget(self):
        return self.component.html_target

    def getURL(self):
        context = self.form.getContentData().getContent()
        return str(absoluteURL(context, self.request))

    def valueToUnicode(self, value):
        return unicode(value)


def register():
    registerSchemaField(PathSchemaField, IPath)
