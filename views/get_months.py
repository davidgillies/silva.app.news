## Script (Python) "get_months"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# I18N stuff
from Products.Silva.i18n import translate as _


months = [ _('Jan'),
           _('Feb'),
           _('Mar'),
           _('Apr'),
           _('May'),
           _('Jun'),
           _('Jul'),
           _('Aug'),
           _('Sep'),
           _('Oct'),
           _('Nov'),
           _('Dec') ]

return [ unicode(m) for m in months ]
