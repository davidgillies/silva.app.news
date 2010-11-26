from five import grok
from zope.interface import Interface
from zope.schema.interfaces import ITextLine
from zope.schema import TextLine
from zeam.form.base.markers import INPUT, DISPLAY
from zeam.form.ztk.fields import (SchemaField, SchemaFieldWidget,
    registerSchemaField)


def register():
    registerSchemaField(RecurrenceSchemaField, IRecurrence)


class IRecurrence(ITextLine):
    """ Recurrence schema interface
    """


class Recurrence(TextLine):
    """ Recurrence Field
    """
    grok.implements(IRecurrence)


class RecurrenceSchemaField(SchemaField):
    """ zeam schema field
    """


class RecurrenceWidgetInput(SchemaFieldWidget):
    grok.adapts(RecurrenceSchemaField, Interface, Interface)
    grok.name(str(INPUT))


class RecurrenceWidgetDisplay(RecurrenceWidgetInput):
    grok.name(str(DISPLAY))
