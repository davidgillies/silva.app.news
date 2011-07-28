# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zeam.form.base.markers import INPUT, DISPLAY
from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zeam.form.ztk.fields import registerSchemaField
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import TextLine
from zope.schema.interfaces import ITextLine

from js.jqueryui import jqueryui
from silva.fanstatic import need
from silva.core import conf as silvaconf


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


class IRecurrenceResources(IDefaultBrowserLayer):
    silvaconf.resource(jqueryui)
    silvaconf.resource('recurrence.js')
    silvaconf.resource('recurrence.css')


class RecurrenceWidgetInput(SchemaFieldWidget):
    grok.adapts(RecurrenceSchemaField, Interface, Interface)
    grok.name(str(INPUT))

    def update(self):
        need(IRecurrenceResources)
        super(RecurrenceWidgetInput, self).update()


class RecurrenceWidgetDisplay(RecurrenceWidgetInput):
    grok.name(str(DISPLAY))


def register():
    registerSchemaField(RecurrenceSchemaField, IRecurrence)
